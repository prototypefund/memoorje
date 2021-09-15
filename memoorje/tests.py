from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from memoorje.models import User


class BaseTestCase(APITestCase):
    base_url = "/api"

    def get_api_url(self, url):
        """
        Prepend the path to the full url for this test class.
        :param url: an url fragment
        :return: the url fragment prepended with the base url
        """
        return f"{self.base_url}{url}"


class UserTestCase(BaseTestCase):
    def setUp(self):
        self.user = User.objects.create_user("test@example.org", "test12345")

    def authenticate_user(self):
        self.client.force_authenticate(user=self.user)


class DjoserBaseTestCase(BaseTestCase):
    base_url = "/api/auth"

    def test_signup(self):
        """
        Create a new user account (signup)
        """
        url = "/users/"
        email = "test@example.org"
        data = {"email": email, "password": "test12345"}
        response = self.client.post(self.get_api_url(url), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, email)


class DjoserJWTTestCase(BaseTestCase):
    base_url = "/api/auth"

    def setUp(self) -> None:
        self.email = "test@example.org"
        self.password = "test12345"
        self.user = User.objects.create_user(self.email, self.password)

    def test_login(self) -> None:
        """
        Obtain JSON Web Tokens (login)
        """
        url = "/jwt/create/"
        data = {"email": self.email, "password": self.password}
        response = self.client.post(self.get_api_url(url), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertSetEqual(set(response.data), {"access", "refresh"})

    def test_get_user(self) -> None:
        """
        Retrieve data of authenticated user
        """
        url = "/users/me/"
        # This test actually covers authentication *and* user data retrieval.
        # self.client.force_authenticate(user=self.user)
        access_token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {access_token}")
        response = self.client.get(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, {"email": self.email, "id": self.user.id})


class APITestCase(UserTestCase):
    def test_create_capsule(self) -> None:
        """
        Create a capsule
        """
        url = "/capsules/"
        response = self.client.post(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.authenticate_user()
        response = self.client.post(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
