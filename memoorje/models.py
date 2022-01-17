from datetime import date
import hashlib
from typing import Any, Mapping, Optional
import uuid

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from djeveric.fields import ConfirmationField
from djeveric.models import ConfirmableModelMixin
from memoorje_crypto.formats import EncryptionV1

from memoorje.data_storage.fields import CapsuleDataField
from memoorje.emails import (
    CapsuleHintsEmail,
    CapsuleReceiverConfirmationEmail,
    CapsuleReceiverReleaseNotificationEmail,
    RecipientsChangedNotificationEmail,
    ReleaseInitiatedNotificationEmail,
    ReminderEmail,
    TrusteePartialKeyInvitationEmail,
)
from memoorje.tokens import CapsuleReceiverTokenGeneratorProxy


def _format_frontend_link(key, **kwargs):
    return settings.FRONTEND_LINKS[key].format(**kwargs)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError("The email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(PermissionsMixin, AbstractBaseUser):
    email = models.EmailField(_("email address"), unique=True)
    name = models.CharField(max_length=100, blank=True)
    remind_interval = models.PositiveSmallIntegerField(default=settings.DEFAULT_REMIND_INTERVAL_MONTHS)
    last_reminder_sent_on = models.DateField(null=True, blank=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def send_email(self, email_class, context):
        """Send an email to this user."""
        email_class(self.email).send(context)

    def send_reminder(self):
        """Send a reminder to this user."""
        self.send_email(ReminderEmail, {})
        self.last_reminder_sent_on = date.today()
        self.save()


class CapsuleContent(models.Model):
    capsule = models.ForeignKey("Capsule", on_delete=models.CASCADE)
    metadata = models.BinaryField()
    data = CapsuleDataField()


class CapsuleReceiverQuerySet(models.QuerySet):
    def get_by_token(self, token: str):
        if token is not None:
            pk, *_ = token.partition("-")
            try:
                receiver: CapsuleReceiver = self.get(pk=int(pk))
                if receiver.receiver_token_generator_proxy.check_token(token):
                    return receiver
                else:
                    raise CapsuleReceiver.DoesNotExist("Invalid token.")
            except ValueError:
                raise CapsuleReceiver.DoesNotExist(f"Invalid pk: {pk}.")
        raise CapsuleReceiver.DoesNotExist("No receiver found for None token.")


class CapsuleReceiver(ConfirmableModelMixin, models.Model):
    capsule = models.ForeignKey("Capsule", on_delete=models.CASCADE, related_name="receivers")
    created_on = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()
    is_email_confirmed = ConfirmationField(email_class=CapsuleReceiverConfirmationEmail)

    objects = models.Manager.from_queryset(CapsuleReceiverQuerySet)()

    class Meta:
        unique_together = ["capsule", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.receiver_token_generator_proxy = CapsuleReceiverTokenGeneratorProxy(self)

    def get_confirmation_email_context(self) -> Mapping[str, Any]:
        return {
            "capsule": self.capsule,
            "confirm_link": _format_frontend_link(
                "capsule_recipient_confirm", pk=self.pk, token=self.make_confirmation_token()
            ),
            "justification_link": _format_frontend_link("capsule_recipient_justify"),
        }

    def is_active(self):
        return self.is_email_confirmed

    def send_release_notification(self, password):
        """Send a capsule release notification to this receiver."""
        context = {
            "password": password,
            "token": self.receiver_token_generator_proxy.make_token(),
        }
        email = CapsuleReceiverReleaseNotificationEmail(self.email)
        email.send(context)


class Keyslot(models.Model):
    class Purpose(models.TextChoices):
        PASSWORD = "pwd"
        SSS = "sss"

    capsule = models.ForeignKey("Capsule", on_delete=models.CASCADE, related_name="keyslots")
    data = models.BinaryField()
    purpose = models.CharField(max_length=3, choices=Purpose.choices)

    def decrypt(self, password: bytes) -> bytes:
        encryption = EncryptionV1()
        return encryption.decrypt(password, self.data)


class PartialKey(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    capsule = models.ForeignKey("Capsule", on_delete=models.CASCADE, related_name="partial_keys")
    data = models.BinaryField()

    @staticmethod
    def hash_key_data(data):
        return hashlib.sha256(data).digest()


class Trustee(models.Model):
    capsule = models.ForeignKey("Capsule", on_delete=models.CASCADE, related_name="trustees")
    email = models.EmailField(blank=True)
    name = models.CharField(max_length=100, blank=True)
    partial_key_hash = models.BinaryField()

    class Meta:
        unique_together = ["capsule", "partial_key_hash"]

    def send_partial_key_invitation(self):
        if self.email:
            TrusteePartialKeyInvitationEmail(self.email).send(
                {
                    "capsule": self.capsule,
                    "justification_link": _format_frontend_link("partial_key_justify"),
                    "partial_key_link": _format_frontend_link("partial_key_create", capsule_pk=self.capsule.pk),
                }
            )


class Capsule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey("User", on_delete=models.CASCADE, related_name="capsules")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_released = models.BooleanField(default=False)
    are_partial_key_invitations_sent = models.BooleanField(default=False)

    # We use a recursive relationship such that the capsule model itself can be handled just like any of the other
    # "capsule related" models (e.g. in views).
    capsule = models.ForeignKey("self", on_delete=models.CASCADE, null=True, related_name="+")

    def touch(self, timestamp=timezone.now()):
        self.updated_on = timestamp
        self.save()

    def release(self) -> Optional[Mapping[CapsuleReceiver, str]]:
        """
        Try to release this capsule. "Releasing" means combining all existing partial keys, decrypting the secret and
        re-encrypting it with a new password.

        Releasing the capsule is only tried if the capsule was not already released and at least one partial key exists.

        :return: A newly created password for each recipient of this capsule. None otherwise.
        """
        from memoorje.crypto import recrypt_capsule

        if not self.is_released:
            partial_keys = self.partial_keys.all()
            if partial_keys.exists():
                passwords = recrypt_capsule(self, partial_keys)
                # We prevent Capsule.updated_on from being touched when setting the is_released flag.
                self._meta.model._default_manager.update(id=self.id, is_released=True)
                return passwords
        return None

    def send_hints(self, inactive_receivers=None):
        """Send hints regarding notable facts to capsule owner."""
        self.owner.send_email(CapsuleHintsEmail, {"inactive_receivers": inactive_receivers})

    def send_notification(self, recipients_changed=False, release_initiated=False):
        """Send a notification email to the capsule owner."""
        if recipients_changed:
            self.owner.send_email(RecipientsChangedNotificationEmail, {})
        if release_initiated:
            self.owner.send_email(ReleaseInitiatedNotificationEmail, {})
