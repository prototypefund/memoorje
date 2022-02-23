import json

from django.conf import settings
from django.core import mail
from rest_framework import status

from memoorje.emails import UserRegistrationConfirmationEmail
from memoorje.models import User
from memoorje.rest_api.tests.utils import format_decimal, MemoorjeAPITestCase
from memoorje.tests.mixins import UserMixin


class UserTestCase(UserMixin, MemoorjeAPITestCase):
    base_url = "/api/auth"

    def test_signup(self):
        """Create a new user account (signup)"""
        email = "test@example.org"
        response = self._register_user(email)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get()
        self.assertEqual(user.email, email)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login(self) -> None:
        """Create a session cookie (login)"""
        self.create_user()
        response = self._login_user(self.email, self.password)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_with_invalid_credentials(self) -> None:
        """Trying to log in with invalid credentials returns an error."""
        self.create_user()
        response = self._login_user(self.email, "invalid password")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content)["code"], "login-invalid")
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout(self) -> None:
        """Remove the session (logout)"""
        url = "/logout/"
        self.authenticate_user()
        response = self.client.post(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_retrieve_user(self) -> None:
        """Retrieve data of authenticated user"""
        url = "/profile/"
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "accountBalance": format_decimal(self.user.transactions.get_balance(), ".01"),
                "email": self.email,
                "id": self.user.id,
                "name": self.user.name,
                "remindInterval": settings.DEFAULT_REMIND_INTERVAL_MONTHS,
            },
        )

    def test_set_remind_interval(self):
        """Set the remind-interval of the authenticated user"""
        url = "/profile/"
        remind_interval = 23
        self.authenticate_user()
        response = self.client.patch(self.get_api_url(url), {"remindInterval": remind_interval})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.remind_interval, remind_interval)

    def test_create_two_users(self) -> None:
        """Create more than one user"""
        self.create_user()
        self.create_user()
        self.assertEqual(User.objects.count(), 2)

    def test_send_registration_email(self):
        self._register_user()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Please confirm your email address", mail.outbox[0].body)

    def test_verify_registration(self):
        self.create_user()
        response = self._verify_user(self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_fails_for_unverified_user(self):
        self._register_user()
        response = self._login_user()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_succeeds_after_verification(self):
        email = "test@example.org"
        password = "test12345"
        self._register_user(email, password)
        self.assertEqual(User.objects.count(), 1)
        self._verify_user(User.objects.get())
        response = self._login_user(email, password)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reset_password_sends_email(self):
        url = "/send-reset-password-link/"
        self.create_user()
        response = self.client.post(self.get_api_url(url), {"login": self.user.email})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Reset your password", mail.outbox[0].body)

    def _register_user(self, email="test@example.org", password="test12345"):
        url = "/register/"
        data = {"email": email, "password": password, "passwordConfirm": password}
        return self.client.post(self.get_api_url(url), data)

    def _verify_user(self, user: User):
        url = "/verify-registration/"
        data = self._get_signed_data(user)
        response = self.client.post(self.get_api_url(url), data)
        return response

    def _login_user(self, email="test@example.org", password="test12345"):
        url = "/login/"
        data = {"login": email, "password": password}
        return self.client.post(self.get_api_url(url), data)

    def _get_signed_data(self, user: User):
        return UserRegistrationConfirmationEmail(None).get_signed_data(user)
