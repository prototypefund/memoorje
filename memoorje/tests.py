from rest_framework import status
from rest_framework.test import APITestCase

from memoorje.models import User


class DjoserBaseTestCase(APITestCase):
    base_url = "/api/auth"

    def get_api_url(self, url):
        """
        Prepend the path to the full url for this test class.
        :param url: an url fragment
        :return: the url fragment prepended with the base url
        """
        return f"{self.base_url}{url}"

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
