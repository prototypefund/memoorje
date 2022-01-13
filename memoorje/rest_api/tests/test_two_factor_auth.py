from binascii import unhexlify
import json

from django_otp.oath import TOTP
from django_otp.plugins.otp_totp.models import default_key
from rest_framework import status
from rest_framework.test import APITestCase

from memoorje.tests.mixins import UserMixin
from memoorje_2fa.users import get_named_device_for_user, is_2fa_enabled_for_user


class TwoFactorUserTestCase(UserMixin, APITestCase):
    def test_login_without_token(self) -> None:
        """Trying to log in to a 2FA account without token returns an error."""
        url = "/api/auth/login/"
        self.create_user(is_2fa_enabled=True)
        data = {"login": self.email, "password": self.password}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"][0].code, "provide-token")
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_with_invalid_token(self) -> None:
        """Trying to log in to a 2FA account with an invalid token returns an error."""
        url = "/api/auth/login/"
        self.create_user(is_2fa_enabled=True)
        data = {"login": self.email, "password": self.password, "token": "012345"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"].code, "login-invalid")
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_with_valid_token(self) -> None:
        """Trying to log in to a 2FA account with a valid token logs the user in successfully."""
        url = "/api/auth/login/"
        self.create_user(is_2fa_enabled=True)
        data = {"login": self.email, "password": self.password, "token": self.two_factor_token}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_enable_2fa_when_already_enabled(self):
        """Trying to enable 2FA when it is already enabled returns an error."""
        url = "/api/auth/two-factor/"
        self.create_user(is_2fa_enabled=True)
        self.authenticate_user()
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["user"][0].code, "already-enabled")

    def test_enable_2fa_unauthorized(self):
        """Enabling 2FA when not logged in returns an error."""
        url = "/api/auth/two-factor/"
        self.create_user()
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(is_2fa_enabled_for_user(self.user))

    def test_enable_2fa_with_invalid_token(self):
        """Enabling 2FA with an invalid combination of key/ token fails."""
        url = "/api/auth/two-factor/"
        data = {"key": "0123456789ABCDEF0123", "token": 123456}
        self.authenticate_user()
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"][0].code, "invalid-token")
        self.assertFalse(is_2fa_enabled_for_user(self.user))

    def test_enable_2fa_with_valid_token(self):
        """Enabling 2FA with a valid combination of key/ token succeeds."""
        url = "/api/auth/two-factor/"
        key = default_key()
        data = {"key": key, "token": TOTP(unhexlify(key.encode())).token()}
        self.authenticate_user()
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(is_2fa_enabled_for_user(self.user))

    def test_retrieve_2fa_status_disabled(self):
        """Issuing a GET on the two-factor endpoint of a user with disabled 2FA should return a 404."""
        url = "/api/auth/two-factor/"
        self.authenticate_user()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_2fa_status_enabled(self):
        """Issuing a GET on the two-factor endpoint of a user with enabled 2FA should return valid data."""
        url = "/api/auth/two-factor/"
        self.create_user(is_2fa_enabled=True)
        self.authenticate_user()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(json.loads(response.content), {"key": self.two_factor_device.key})

    def test_disable_2fa(self):
        """2FA can be disabled with DELETE two-factor."""
        url = "/api/auth/two-factor/"
        self.create_user(is_2fa_enabled=True)
        self.authenticate_user()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(is_2fa_enabled_for_user(self.user))

    def test_create_backup_tokens(self):
        """Create a set of backup tokens."""
        url = "/api/auth/two-factor/backup-tokens/"
        self.create_user(is_2fa_enabled=True)
        self.authenticate_user()
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertDictEqual(
            json.loads(response.content),
            {"tokens": list(get_named_device_for_user(self.user, "backup").token_set.values_list("token", flat=True))},
        )
