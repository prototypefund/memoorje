from rest_framework import status

from memoorje.models import User
from memoorje.rest_api.tests.memoorje import MemoorjeAPITestCase
from memoorje.tests import UserMixin


class UserTestCase(UserMixin, MemoorjeAPITestCase):
    base_url = "/api/auth"

    def test_signup(self):
        """
        Create a new user account (signup)
        """
        url = "/register/"
        email = "test@example.org"
        password = "test12345"
        data = {"email": email, "password": password, "passwordConfirm": password}
        response = self.client.post(self.get_api_url(url), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, email)

    def test_login(self) -> None:
        """
        Create a session cookie (login)
        """
        url = "/login/"
        self.create_user()
        data = {"login": self.email, "password": self.password}
        response = self.client.post(self.get_api_url(url), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.wsgi_request.email.is_authenticated)

    def test_logout(self) -> None:
        """
        Remove the session (logout)
        """
        url = "/logout/"
        self.authenticate_user()
        response = self.client.post(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.wsgi_request.email.is_authenticated)

    def test_retrieve_user(self) -> None:
        """
        Retrieve data of authenticated user
        """
        url = "/profile/"
        self.create_user()
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            response.data,
            {
                "email": self.email,
                "id": self.user.id,
                "name": self.user.name,
            },
        )

    def test_create_two_users(self) -> None:
        """
        Create more than one user
        """
        self.create_user()
        self.create_user()
        self.assertEqual(User.objects.count(), 2)
