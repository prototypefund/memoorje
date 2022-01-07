from rest_framework import status
from rest_framework.test import APITestCase

from memoorje.tests.mixins import UserMixin


class TwoFactorUserTestCase(UserMixin, APITestCase):
    def test_login_without_token(self) -> None:
        """Trying to login to a 2FA account without token returns an error."""
        url = "/api/auth/login/"
        self.create_user(two_factor=True)
        data = {"login": self.email, "password": self.password}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"][0].code, "provide-token")
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_with_invalid_token(self) -> None:
        """Trying to login to a 2FA account with an invalid token returns an error."""
        url = "/api/auth/login/"
        self.create_user(two_factor=True)
        data = {"login": self.email, "password": self.password, "token": "012345"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"].code, "login-invalid")
        self.assertFalse(response.wsgi_request.user.is_authenticated)
