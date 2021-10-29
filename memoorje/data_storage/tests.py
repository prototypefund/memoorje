from django.test import TestCase
from rest_framework import status

from memoorje.tests.mixins import CapsuleContentMixin


class CapsuleContentTestCase(CapsuleContentMixin, TestCase):
    def test_download_data(self):
        """
        Download the file for a capsule content.
        """
        self.create_capsule_content()
        url = self.capsule_content.data.url
        self.authenticate_user()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(b"".join(response.streaming_content), self.data)

    def test_download_data_unauthorized(self):
        """
        Try to download the file for a capsule content belonging to another user.
        """
        self.create_capsule_content()
        url = self.capsule_content.data.url
        self.create_user()
        self.authenticate_user()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
