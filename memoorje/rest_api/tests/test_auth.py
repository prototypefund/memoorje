import json

from django.conf import settings
from rest_framework import status

from memoorje.models import User
from memoorje.rest_api.tests.utils import MemoorjeAPITestCase
from memoorje.tests.mixins import UserMixin


class UserTestCase(UserMixin, MemoorjeAPITestCase):
    base_url = "/api/auth"

    def test_signup(self):
        """Create a new user account (signup)"""
        url = "/register/"
        email = "test@example.org"
        password = "test12345"
        data = {"email": email, "password": password, "passwordConfirm": password}
        response = self.client.post(self.get_api_url(url), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get()
        self.assertEqual(user.email, email)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login(self) -> None:
        """Create a session cookie (login)"""
        url = "/login/"
        self.create_user()
        data = {"login": self.email, "password": self.password}
        response = self.client.post(self.get_api_url(url), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_with_invalid_credentials(self) -> None:
        """Trying to login with invalid credentials returns an error."""
        url = "/login/"
        self.create_user()
        data = {"login": self.email, "password": "invalid"}
        response = self.client.post(self.get_api_url(url), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"].code, "login-invalid")
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
                "accountBalance": str(self.user.transactions.get_balance()),
                "email": self.email,
                "id": self.user.id,
                "name": self.user.name,
                "remindInterval": settings.DEFAULT_REMIND_INTERVAL_MONTHS,
            },
        )

    def test_set_remind_interval(self):
        """Set the remind interval of the authenticated user"""
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
