from django.conf import settings
from django.db import transaction
from django_otp import devices_for_user
from django_otp.plugins.otp_static.models import StaticToken
from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_registration.exceptions import UserNotFound
from rest_registration.utils.users import authenticate_by_login_data


def authenticate(data, **kwargs):
    user = authenticate_by_login_data(data, **kwargs)
    if is_2fa_enabled_for_user(user):
        serializer = kwargs.get("serializer")
        is_not_found_error = False
        with transaction.atomic():
            if serializer and serializer.is_valid():
                device = get_default_device_for_user(user)
                if not device.verify_token(serializer.validated_data["token"]):
                    is_not_found_error = True
            else:
                is_not_found_error = True
        if is_not_found_error:
            raise UserNotFound()
    return user


def create_backup_tokens_for_user(user):
    device, _ = user.staticdevice_set.get_or_create(name="backup")
    device.token_set.all().delete()
    for _ in range(settings.TWO_FACTOR_BACKUP_TOKEN_COUNT):
        device.token_set.create(token=StaticToken.random_token())
    return device


def create_default_device_for_user(user, **kwargs):
    return TOTPDevice.objects.create(name="default", user=user, **kwargs)


def get_named_device_for_user(user, name):
    for device in devices_for_user(user):
        if device.name == name:
            return device


def get_default_device_for_user(user):
    return get_named_device_for_user(user, "default")


def is_2fa_enabled_for_user(user):
    """Returns True, if two-factor authentication is enabled for the given user."""
    return get_default_device_for_user(user) is not None
