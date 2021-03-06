from base64 import b64encode
import json
import os

from rest_framework import status

from memoorje.models import CapsuleContent
from memoorje.rest_api.tests.utils import MemoorjeAPITestCase, reverse
from memoorje.tests.memoorje import create_test_data_file
from memoorje.tests.mixins import CapsuleContentMixin, CapsuleRecipientMixin


class CapsuleContentTestCase(CapsuleContentMixin, MemoorjeAPITestCase):
    def test_access_contents_without_capsule(self):
        """
        Access capsule content list without a capsule given
        """
        url = "/capsule-contents/"
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.data, [])

    def test_create_capsule_content(self):
        """Create a content for an existing capsule"""
        url = "/capsule-contents/"
        metadata = b"Capsule Content's Metadata"
        data = b"Capsule Content's File Data"
        self.create_capsule()
        self.authenticate_user()
        with create_test_data_file(data) as data_file:
            with create_test_data_file(metadata) as metadata_file:
                response = self.client.post(
                    self.get_api_url(url),
                    {
                        "capsule": reverse("capsule", self.capsule),
                        "metadata": metadata_file,
                        "data": data_file,
                    },
                    format="multipart",
                )
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                self.assertEqual(CapsuleContent.objects.count(), 1)
                capsule_content = CapsuleContent.objects.get()
                self.assertEqual(capsule_content.capsule, self.capsule)
                self.assertEqual(capsule_content.metadata, metadata)
                self.assertEqual(capsule_content.data.read(), data)

    def test_create_capsule_content_unauthorized(self):
        """
        Create a content for a capsule belonging to another user.
        """

        def request(request_url, request_body):
            request_body["metadata"].seek(0)
            request_body["data"].seek(0)
            return self.client.post(self.get_api_url(request_url), request_body, format="multipart")

        url = "/capsule-contents/"
        self.create_capsule()
        with create_test_data_file(b"test") as data_file:
            with create_test_data_file(b"test") as metadata_file:
                request_data = {
                    "capsule": reverse("capsule", self.capsule),
                    "metadata": metadata_file,
                    "data": data_file,
                }
                self.authenticate_user()
                response = request(url, request_data)
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                self.create_user()
                self.authenticate_user()
                response = request(url, request_data)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_modify_capsule(self):
        """
        Any capsule and capsule content modifications should update the capsule's update timestamp.
        """
        self.create_capsule()

        # change an attribute of the capsule itself
        initial_updated_on = self.capsule.updated_on
        self.authenticate_user()
        self.client.patch(self.get_api_url("/capsules/{pk}/", pk=self.capsule.pk), {"name": "Changed the name"})
        self.capsule.refresh_from_db()
        self.assertGreater(self.capsule.updated_on, initial_updated_on)

        # modify capsule's content
        initial_updated_on = self.capsule.updated_on
        self.create_capsule_content()
        self.assertGreater(self.capsule.updated_on, initial_updated_on)
        initial_updated_on = self.capsule.updated_on
        self.capsule_content.delete()
        self.assertGreater(self.capsule.updated_on, initial_updated_on)

    def test_list_capsule_contents(self):
        """
        List the contents for a capsule.
        """
        url = "/capsule-contents/?capsule={pk}"
        self.create_capsule_content()
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url, pk=self.capsule.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            json.loads(response.content),
            [
                {
                    "capsule": reverse("capsule", self.capsule, response),
                    "data": response.wsgi_request.build_absolute_uri(self.capsule_content.data.url),
                    "dataSizeBytes": self.capsule_content.data.size,
                    "id": self.capsule_content.id,
                    "metadata": b64encode(self.metadata).decode(),
                    "url": reverse("capsulecontent", self.capsule_content, response),
                },
            ],
        )

    def test_delete_capsule_content(self):
        """
        Delete a capsule content.
        """
        url = "/capsule-contents/{pk}/"
        self.create_capsule_content()
        self.authenticate_user()
        file_path = self.capsule_content.data.path
        response = self.client.delete(self.get_api_url(url, pk=self.capsule_content.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CapsuleContent.objects.exists())
        self.assertFalse(os.path.isfile(file_path))

    def test_update_capsule_content_metadata(self):
        """
        Update the metadata field of a capsule content.
        """
        url = "/capsule-contents/{pk}/"
        metadata = b"Some test metadata (updated)"
        self.create_capsule_content()
        self.authenticate_user()
        with create_test_data_file(metadata) as metadata_file:
            response = self.client.patch(
                self.get_api_url(url, pk=self.capsule_content.pk),
                {
                    "metadata": metadata_file,
                },
                format="multipart",
            )
            self.capsule_content.refresh_from_db()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(self.capsule_content.metadata, metadata)

    def test_list_all_capsule_contents(self):
        """
        List all accessible contents for a capsule.
        """
        url = "/capsule-contents/"
        self.create_capsule_content()
        self.create_user()
        self.create_capsule_content()
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class CapsuleContentAccessWithRecipientTokenTestCase(CapsuleContentMixin, CapsuleRecipientMixin, MemoorjeAPITestCase):
    def test_retrieve_capsule_content(self):
        """Gain access to a capsule content by providing a recipient token."""
        url = "/capsule-contents/{pk}/"
        self.create_capsule_content()
        self.create_capsule_recipient()
        response = self.client.get(
            self.get_api_url(url, pk=self.capsule_content.pk),
            **self.get_request_headers(with_recipient_token_for=self.capsule_recipient),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
