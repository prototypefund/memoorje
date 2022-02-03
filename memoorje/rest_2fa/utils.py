from django.conf import settings
from django_otp.oath import TOTP


def get_totp_for_device(device):
    return TOTP(device.bin_key, device.step, device.t0, device.digits, device.drift)


def get_token_max_value():
    digits = getattr(settings, "MEMOORJE_2FA_TOTP_DIGITS", 6)
    return 10**digits - 1
