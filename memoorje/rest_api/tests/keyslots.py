from base64 import b64encode
import json

from rest_framework import status
from rest_framework.reverse import reverse

from memoorje.models import Keyslot
from memoorje.rest_api.tests.memoorje import create_test_data_file, get_url, MemoorjeAPITestCase
from memoorje.rest_api.tests.mixins import CapsuleMixin, KeyslotMixin


class KeyslotTestCase(KeyslotMixin, MemoorjeAPITestCase):
    def test_access_keyslots_without_capsule(self):
        """Access keyslot list without a capsule given"""
        url = "/keyslots/"
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.data, [])

    def test_create_keyslot(self):
        """Create a keyslot for an existing capsule"""
        url = "/keyslots/"
        data = b"Keyslot's Data"
        purpose = "pwd"
        self.create_capsule()
        self.authenticate_user()
        with create_test_data_file(data) as data_file:
            response = self.client.post(
                self.get_api_url(url),
                {
                    "capsule": get_url("capsule", self.capsule),
                    "data": data_file,
                    "purpose": purpose,
                },
                format="multipart",
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Keyslot.objects.count(), 1)
            keyslot = Keyslot.objects.get()
            self.assertEqual(keyslot.capsule, self.capsule)
            self.assertEqual(keyslot.data, data)
            self.assertEqual(keyslot.purpose, purpose)

    # def test_modify_capsule(self):
    #     """
    #     Any capsule and capsule content modifications should update the capsule's update timestamp.
    #     """
    #     self.create_capsule()
    #
    #     # change an attribute of the capsule itself
    #     initial_updated_on = self.capsule.updated_on
    #     self.authenticate_user()
    #     self.client.patch(self.get_api_url("/capsules/{pk}/", pk=self.capsule.pk), {"name": "Changed the name"})
    #     self.capsule.refresh_from_db()
    #     self.assertGreater(self.capsule.updated_on, initial_updated_on)
    #
    #     # modify capsule's content
    #     initial_updated_on = self.capsule.updated_on
    #     self.create_capsule_content()
    #     self.assertGreater(self.capsule.updated_on, initial_updated_on)
    #     initial_updated_on = self.capsule.updated_on
    #     self.capsule_content.delete()
    #     self.assertGreater(self.capsule.updated_on, initial_updated_on)

    def test_list_keyslots(self):
        """List the keyslots for a capsule."""
        url = "/keyslots/?capsule={pk}"
        self.create_keyslot()
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url, pk=self.capsule.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            json.loads(response.content),
            [
                {
                    "capsule": get_url("capsule", self.capsule, response),
                    "id": self.keyslot.id,
                    "data": b64encode(self.data).decode(),
                    "purpose": self.purpose,
                    "url": get_url("keyslot", self.keyslot, response),
                },
            ],
        )

    # def test_delete_capsule_content(self):
    #     """
    #     Delete a capsule content.
    #     """
    #     url = "/capsule-contents/{pk}/"
    #     self.create_capsule_content()
    #     self.authenticate_user()
    #     file_path = self.capsule_content.data.path
    #     response = self.client.delete(self.get_api_url(url, pk=self.capsule_content.pk))
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    #     self.assertFalse(CapsuleContent.objects.exists())
    #     self.assertFalse(os.path.isfile(file_path))
    #
    # def test_update_capsule_content_metadata(self):
    #     """
    #     Update the metadata field of a capsule content.
    #     """
    #     url = "/capsule-contents/{pk}/"
    #     metadata = b"Some test metadata (updated)"
    #     self.create_capsule_content()
    #     self.authenticate_user()
    #     with create_test_data_file(metadata) as metadata_file:
    #         response = self.client.patch(
    #             self.get_api_url(url, pk=self.capsule_content.pk),
    #             {
    #                 "metadata": metadata_file,
    #             },
    #             format="multipart",
    #         )
    #         self.capsule_content.refresh_from_db()
    #         self.assertEqual(response.status_code, status.HTTP_200_OK)
    #         self.assertEqual(self.capsule_content.metadata, metadata)
