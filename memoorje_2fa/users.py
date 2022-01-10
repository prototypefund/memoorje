from django_otp import devices_for_user
from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_registration.exceptions import UserNotFound
from rest_registration.utils.users import authenticate_by_login_data


def authenticate(data, **kwargs):
    user = authenticate_by_login_data(data, **kwargs)
    if is_2fa_enabled_for_user(user):
        serializer = kwargs.get("serializer")
        if serializer and serializer.is_valid():
            device = get_default_device_for_user(user)
            if not device.verify_token(serializer.validated_data["token"]):
                raise UserNotFound()
        else:
            raise UserNotFound()
    return user


def create_default_device_for_user(user):
    return TOTPDevice.objects.create(name="default", user=user)


def get_default_device_for_user(user) -> TOTPDevice:
    for device in devices_for_user(user):
        if device.name == "default":
            return device


def is_2fa_enabled_for_user(user):
    """Returns True, if two-factor authentication is enabled for the given user."""
    return get_default_device_for_user(user) is not None
