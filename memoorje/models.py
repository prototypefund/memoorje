from datetime import date
import hashlib
from typing import Mapping, Optional
import uuid

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from djeveric.fields import ConfirmationField
from djeveric.models import ConfirmableModelMixin
from memoorje_crypto.formats import EncryptionV1

from memoorje.data_storage.fields import CapsuleDataField
from memoorje.emails import (
    CapsuleHintsEmail,
    CapsuleRecipientConfirmationEmail,
    CapsuleRecipientReleaseNotificationEmail,
    JournalNotificationEmail,
    ReleaseInitiatedNotificationEmail,
    ReminderEmail,
    TrusteePartialKeyInvitationEmail,
    UserRegistrationConfirmationEmail,
)
from memoorje.tokens import CapsuleRecipientTokenGeneratorProxy


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
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    latest_notified_journal_entry = models.OneToOneField(
        "JournalEntry", on_delete=models.SET_NULL, null=True, related_name="+"
    )

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

    def send_email(self, email_class, **kwargs):
        """Send an email to this user."""
        email_class(self.email).send(**kwargs)

    def send_journal_notification(self):
        """Send a notification on new journal entries to this user."""
        self.send_email(JournalNotificationEmail)

    def send_registration_confirmation(self):
        """Send a confirmation email to this user."""
        self.send_email(UserRegistrationConfirmationEmail, instance=self)

    def send_reminder(self):
        """Send a reminder to this user."""
        self.send_email(ReminderEmail, instance=self)
        self.last_reminder_sent_on = date.today()
        self.save()


class CapsuleContent(models.Model):
    capsule = models.ForeignKey("Capsule", on_delete=models.CASCADE)
    metadata = models.BinaryField()
    data = CapsuleDataField()


class CapsuleRecipientQuerySet(models.QuerySet):
    def get_by_token(self, token: str):
        if token is not None:
            pk, *_ = token.partition("-")
            try:
                recipient: CapsuleRecipient = self.get(pk=int(pk))
                if recipient.recipient_token_generator_proxy.check_token(token):
                    return recipient
                else:
                    raise CapsuleRecipient.DoesNotExist("Invalid token.")
            except ValueError:
                raise CapsuleRecipient.DoesNotExist(f"Invalid pk: {pk}.")
        raise CapsuleRecipient.DoesNotExist("No recipient found for None token.")


class CapsuleRecipient(ConfirmableModelMixin, models.Model):
    capsule = models.ForeignKey("Capsule", on_delete=models.CASCADE, related_name="recipients")
    created_on = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()
    is_email_confirmed = ConfirmationField(email_class=CapsuleRecipientConfirmationEmail)
    name = models.CharField(max_length=100, blank=True)

    objects = models.Manager.from_queryset(CapsuleRecipientQuerySet)()

    class Meta:
        unique_together = ["capsule", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recipient_token_generator_proxy = CapsuleRecipientTokenGeneratorProxy(self)

    def is_active(self) -> bool:
        return self.is_email_confirmed

    def send_release_notification(self, password):
        """Send a capsule release notification to this recipient."""
        CapsuleRecipientReleaseNotificationEmail(self.email).send(instance=self, password=password)


class Keyslot(models.Model):
    class Purpose(models.TextChoices):
        PASSWORD = "pwd"
        SSS = "sss"

    capsule = models.ForeignKey("Capsule", on_delete=models.CASCADE, related_name="keyslots")
    data = models.BinaryField()
    purpose = models.CharField(max_length=3, choices=Purpose.choices)
    recipient = models.OneToOneField("CapsuleRecipient", on_delete=models.CASCADE, null=True)

    def decrypt(self, password: bytes) -> bytes:
        encryption = EncryptionV1()
        return encryption.decrypt(password, self.data)


class PartialKey(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    capsule = models.ForeignKey("Capsule", on_delete=models.CASCADE, related_name="partial_keys")
    data = models.BinaryField()

    class Meta:
        unique_together = ["capsule", "data"]

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
            TrusteePartialKeyInvitationEmail(self.email).send(instance=self)


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

    def release(self) -> Optional[Mapping[CapsuleRecipient, str]]:
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
                Capsule.objects.filter(id=self.id).update(is_released=True)
                return passwords
        return None

    def send_hints(self, inactive_recipients=None):
        """Send hints regarding notable facts to capsule owner."""
        self.owner.send_email(CapsuleHintsEmail, instance=self, inactive_recipients=inactive_recipients)

    def send_notification(self, release_initiated=False):
        """Send a notification email to the capsule owner."""
        if release_initiated:
            self.owner.send_email(ReleaseInitiatedNotificationEmail, instance=self)


class JournalEntry(models.Model):
    class Action(models.TextChoices):
        CREATE = "c"
        UPDATE = "u"
        DELETE = "d"

    created_on = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="journal_entries")
    capsule = models.ForeignKey("Capsule", on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=1, choices=Action.choices)
    entity = GenericForeignKey("entity_type", "entity_id")
    entity_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    entity_id = models.PositiveIntegerField()
