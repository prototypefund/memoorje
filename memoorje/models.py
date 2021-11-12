from datetime import date
import hashlib
from typing import Iterable
import uuid

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from djeveric.fields import ConfirmationField
from djeveric.models import ConfirmableModelMixin

from memoorje.data_storage.fields import CapsuleDataField
from memoorje.emails import CapsuleReceiverConfirmationEmail, ReminderEmail


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
    remind_interval = models.PositiveSmallIntegerField(default=settings.DEFAULT_REMIND_INTERVAL)
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


class Capsule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey("User", on_delete=models.CASCADE, related_name="capsules")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def touch(self, timestamp=timezone.now()):
        self.updated_on = timestamp
        self.save()


class CapsuleContent(models.Model):
    capsule = models.ForeignKey("Capsule", on_delete=models.CASCADE)
    metadata = models.BinaryField()
    data = CapsuleDataField()


class TokenGenerator(PasswordResetTokenGenerator):
    def __init__(self, proxy):
        super().__init__()
        self.proxy = proxy

    def _make_hash_value(self, instance, timestamp):
        data = list(self.proxy.get_token_data())
        assert all(
            isinstance(item, str) for item in data
        ), f"Iterable returned by {instance.__class__.__name__}.get_confirmation_token_data must contain strings."
        serialized_data = "".join(data)
        return f"{serialized_data}{timestamp}"


class CapsuleReceiverAuthenticationTokenGeneratorProxy:
    token_generator_class = TokenGenerator

    def __init__(self, instance):
        self.instance = instance
        self.token_generator = self.token_generator_class(proxy=self)

    def check_token(self, token: str):
        *_, token = token.partition("-")
        return self.token_generator.check_token(self.instance, token)

    def make_token(self):
        return "{}-{}".format(self.instance.pk, self.token_generator.make_token(self.instance))

    def get_token_data(self) -> Iterable[str]:
        return [
            # The pk of the capsule receiver ensures that users get access only to the capsule for this receiver.
            # If the receiver is revoked, the token gets invalid.
            str(self.instance.pk),
            # The access is read-only for a given state of the capsule. If the capsule was changed (which shouldn't
            # happen), access will be denied.
            str(self.instance.capsule.updated_on),
        ]


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
    email = models.EmailField()
    is_email_confirmed = ConfirmationField(email_class=CapsuleReceiverConfirmationEmail)

    objects = models.Manager.from_queryset(CapsuleReceiverQuerySet)()

    class Meta:
        unique_together = ["capsule", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.receiver_token_generator_proxy = CapsuleReceiverAuthenticationTokenGeneratorProxy(self)


class Keyslot(models.Model):
    class Purpose(models.TextChoices):
        PASSWORD = "pwd"
        SSS = "sss"

    capsule = models.ForeignKey("Capsule", on_delete=models.CASCADE)
    data = models.BinaryField()
    purpose = models.CharField(max_length=3, choices=Purpose.choices)


class PartialKey(models.Model):
    capsule = models.ForeignKey("Capsule", on_delete=models.CASCADE)
    data = models.BinaryField()

    @staticmethod
    def hash_key_data(data):
        return hashlib.sha256(data).digest()


class Trustee(models.Model):
    capsule = models.ForeignKey("Capsule", on_delete=models.CASCADE)
    email = models.EmailField(blank=True)
    name = models.CharField(max_length=100, blank=True)
    partial_key_hash = models.BinaryField()

    class Meta:
        unique_together = ["capsule", "partial_key_hash"]
