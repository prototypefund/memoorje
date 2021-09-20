import json
import unittest

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from memoorje.crypto import EncryptionV1
from memoorje.models import Capsule, CapsuleContent, User


class BaseTestCase(APITestCase):
    base_url = "/api"

    def get_api_url(self, url, **kwargs):
        """
        Prepend the path to the full url for this test class.
        :param url: an url fragment
        :return: the url fragment prepended with the base url
        """
        return f"{self.base_url}{url.format(**kwargs)}"


class UserMixin:
    user: User
    password: str
    email: str

    def create_user(self):
        self.email = f"test{User.objects.count()}@example.org"
        self.password = "test12345"
        self.user = User.objects.create_user(self.email, self.password)

    def ensure_user_exists(self):
        if not hasattr(self, "user"):
            self.create_user()

    def authenticate_user(self):
        self.ensure_user_exists()
        self.client.force_authenticate(user=self.user)


class UserTestCase(UserMixin, BaseTestCase):
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

    def test_login(self) -> None:
        """
        Obtain JSON Web Tokens (login)
        """
        url = "/jwt/create/"
        self.create_user()
        data = {"email": self.email, "password": self.password}
        response = self.client.post(self.get_api_url(url), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertSetEqual(set(response.data), {"access", "refresh"})

    def test_retrieve_user(self) -> None:
        """
        Retrieve data of authenticated user
        """
        url = "/users/me/"
        self.create_user()
        # This test actually covers authentication *and* user data retrieval.
        access_token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {access_token}")
        response = self.client.get(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, {"email": self.email, "id": self.user.id})

    def test_create_two_users(self) -> None:
        """
        Create more than one user
        """
        self.create_user()
        self.create_user()
        self.assertEqual(User.objects.count(), 2)


class CapsuleMixin(UserMixin):
    capsule: Capsule
    capsule_description: str
    capsule_name: str

    def create_capsule(self) -> Capsule:
        self.ensure_user_exists()
        self.capsule_name = "test"
        self.capsule_description = "test"
        self.capsule = Capsule.objects.create(
            owner=self.user, name=self.capsule_name, description=self.capsule_description
        )
        return self.capsule


class CapsuleTestCase(CapsuleMixin, BaseTestCase):
    def test_create_capsule_unauthorized(self) -> None:
        """
        Create a capsule unauthorized
        """
        url = "/capsules/"
        response = self.client.post(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_capsule(self) -> None:
        """
        Create a capsule
        """
        url = "/capsules/"
        self.authenticate_user()
        response = self.client.post(self.get_api_url(url), data={"name": "test", "description": "test"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Capsule.objects.count(), 1)
        self.assertEqual(Capsule.objects.get().owner, self.user)

    def test_retrieve_capsule_unauthorized(self) -> None:
        """
        Retrieve a capsule unauthorized
        """
        url = "/capsules/{id}/"
        self.create_capsule()
        response = self.client.post(self.get_api_url(url, id=self.capsule.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_capsule(self) -> None:
        """
        Retrieve a capsule
        """
        url = "/capsules/{id}/"
        self.create_capsule()
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url, id=self.capsule.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "url": reverse("capsule-detail", args=[self.capsule.pk], request=response.wsgi_request),
                "createdOn": self.capsule.created_on.isoformat()[:-6] + "Z",
                "updatedOn": self.capsule.updated_on.isoformat()[:-6] + "Z",
                "name": self.capsule_name,
                "description": self.capsule_description,
            },
        )

    def test_retrieve_others_capsule(self) -> None:
        """
        Retrieve a capsule which does not belong to the logged in user
        """
        url = "/capsules/{pk}/"
        other_capsule = self.create_capsule()
        self.create_user()
        self.create_capsule()
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url, pk=other_capsule.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CapsuleContentTestCase(CapsuleMixin, BaseTestCase):
    def test_access_contents_without_capsule(self):
        """
        Access capsule content list without a capsule given
        """
        url = "/capsule-contents/"
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.post(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_capsule_content(self):
        """
        Create a content for an existing capsule
        """
        url = "/capsule-contents/?capsule={pk}"
        self.create_capsule()
        self.authenticate_user()
        response = self.client.post(self.get_api_url(url, pk=self.capsule.pk))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CapsuleContent.objects.count(), 1)
        self.assertEqual(CapsuleContent.objects.get().capsule, self.capsule)


class EncryptionV1Test(unittest.TestCase):
    def test_encrypted_data_can_be_decrypted(self):
        data = b"my encrypted data"
        password = "abc123"
        encryption = EncryptionV1(iv_size_bytes=64)
        encrypted_data = encryption.encrypt(password, data)
        self.assertTrue(
            EncryptionV1.does_handle_data_stream(encrypted_data),
            "EncryptionV1 should handle its own encrypted data",
        )
        self.assertEqual(
            data,
            EncryptionV1.decrypt(password, encrypted_data),
            "Data encrypted by EncryptionV1 must also be decipherable by it.",
        )
