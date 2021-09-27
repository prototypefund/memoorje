from base64 import b64encode
from contextlib import contextmanager
import json
from tempfile import TemporaryFile

from rest_framework import status
from rest_framework.reverse import reverse

from memoorje.models import CapsuleContent
from memoorje.rest_api.tests import MemoorjeAPITestCase
from memoorje.rest_api.tests.capsules import CapsuleMixin


@contextmanager
def test_data_file(data):
    with TemporaryFile() as f:
        f.write(data)
        f.seek(0)
        yield f


class CapsuleContentMixin(CapsuleMixin):
    capsule_content: CapsuleContent
    data: bytes
    metadata: bytes

    def create_capsule_content(self):
        self.ensure_capsule_exists()
        self.metadata = b"Just any arbitrary metadata (encrypted)"
        self.data = b"Some encrypted data"
        self.capsule_content = CapsuleContent.objects.create(capsule=self.capsule, metadata=self.metadata)
        with test_data_file(self.data) as f:
            self.capsule_content.data.save("testfile", f)


class CapsuleContentTestCase(CapsuleContentMixin, MemoorjeAPITestCase):
    def test_access_contents_without_capsule(self):
        """
        Access capsule content list without a capsule given
        """
        url = "/capsule-contents/"
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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
                    "data": reverse(
                        "capsule-content-data", args=[self.capsule_content.pk], request=response.wsgi_request
                    ),
                },
            ],
        )

    def test_download_data(self):
        """
        Download the file for a capsule content.
        """
        self.create_capsule_content()
        url = reverse("capsule-content-data", args=[self.capsule_content.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(b"".join(response.streaming_content), self.data)
