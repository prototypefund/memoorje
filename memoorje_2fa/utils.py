from django.conf import settings
from django_otp.oath import TOTP
from django_otp.plugins.otp_totp.models import TOTPDevice


def get_token_for_device(device: TOTPDevice):
    totp = TOTP(device.bin_key, device.step, device.t0, device.digits, device.drift)
    return totp.token()


def get_token_max_value():
    digits = getattr(settings, "MEMOORJE_2FA_TOTP_DIGITS", 6)
    return 10 ** digits - 1
