from base64 import b64encode
import json

from rest_framework import status

from memoorje.models import Keyslot
from memoorje.rest_api.tests.memoorje import get_url, MemoorjeAPITestCase
from memoorje.tests.memoorje import create_test_data_file
from memoorje.tests.mixins import KeyslotMixin


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

    def test_create_keyslot_unauthorized(self):
        """Create a keyslot for a capsule belonging to another user."""
        url = "/keyslots/"
        # create a capsule (and an user)
        self.create_capsule()
        # create another user
        self.create_user()
        self.authenticate_user()
        response = self.client.post(
            self.get_api_url(url),
            {
                "capsule": get_url("capsule", self.capsule),
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["capsule"][0].code, "does_not_exist")

    def test_modify_keyslot(self):
        """Any keyslot modifications should update the capsule's update timestamp."""
        self.create_capsule()
        initial_updated_on = self.capsule.updated_on
        self.create_keyslot()
        self.assertGreater(self.capsule.updated_on, initial_updated_on)
        initial_updated_on = self.capsule.updated_on
        self.keyslot.delete()
        self.assertGreater(self.capsule.updated_on, initial_updated_on)

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

    def test_delete_keyslot(self):
        """Delete a keyslot."""
        url = "/keyslots/{pk}/"
        self.create_keyslot()
        self.authenticate_user()
        response = self.client.delete(self.get_api_url(url, pk=self.keyslot.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Keyslot.objects.exists())

    def test_update_keyslot(self):
        """Update the fields of a keyslot."""
        url = "/keyslots/{pk}/"
        data = b"Some test data (updated)"
        purpose = Keyslot.Purpose.SSS
        self.create_keyslot()
        self.authenticate_user()
        with create_test_data_file(data) as data_file:
            response = self.client.put(
                self.get_api_url(url, pk=self.keyslot.pk),
                {
                    "capsule": get_url("capsule", self.capsule),
                    "data": data_file,
                    "purpose": purpose,
                },
                format="multipart",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.keyslot.refresh_from_db()
            self.assertEqual(self.keyslot.data, data)
            self.assertEqual(self.keyslot.purpose, purpose)