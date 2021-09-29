from base64 import b64encode
import json
import os

from rest_framework import status

from memoorje.models import CapsuleContent
from memoorje.rest_api.tests import MemoorjeAPITestCase
from memoorje.tests import CapsuleContentMixin, test_data_file


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
        """
        Create a content for an existing capsule
        """
        url = "/capsule-contents/"
        metadata = b"Capsule Content's Metadata"
        data = b"Capsule Content's File Data"
        self.create_capsule()
        self.authenticate_user()
        with test_data_file(data) as data_file:
            response = self.client.post(
                self.get_api_url(url),
                {
                    "capsule": self.get_capsule_url(),
                    "metadata": b64encode(metadata).decode(),
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
            request_body["data"].seek(0)
            return self.client.post(self.get_api_url(request_url), request_body, format="multipart")

        url = "/capsule-contents/"
        self.create_capsule()
        with test_data_file(b"test") as data_file:
            request_data = {
                "capsule": self.get_capsule_url(),
                "metadata": b64encode(b"test").decode(),
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
        # TODO: we might want to change this to an API request
        self.capsule.name = "Changed the name"
        self.capsule.save()
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
                    "capsule": self.get_capsule_url(response=response),
                    "metadata": b64encode(self.metadata).decode(),
                    "data": response.wsgi_request.build_absolute_uri(self.capsule_content.data.url),
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
