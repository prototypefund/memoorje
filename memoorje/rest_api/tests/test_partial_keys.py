from rest_framework import status

from memoorje.models import PartialKey
from memoorje.rest_api.tests.utils import MemoorjeAPITestCase, reverse
from memoorje.tests.memoorje import create_test_data_file
from memoorje.tests.mixins import TrusteeMixin


class PartialKeyTestCase(TrusteeMixin, MemoorjeAPITestCase):
    def test_create_partial_key_without_registered_hash(self):
        """Disposing a partial key should fail, if no hash for the key data is existing."""
        url = "/partial-keys/"
        data = b"Whatever data"
        self.create_capsule()
        with create_test_data_file(data) as data_file:
            response = self.client.post(
                self.get_api_url(url),
                {
                    "capsule": reverse("capsule", self.capsule),
                    "data": data_file,
                },
                format="multipart",
            )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"][0].code, "invalid_key")

    def test_create_partial_key(self):
        url = "/partial-keys/"
        self.create_trustee()
        with create_test_data_file(self.partial_key_data) as data_file:
            response = self.client.post(
                self.get_api_url(url),
                {
                    "capsule": reverse("capsule", self.capsule),
                    "data": data_file,
                },
                format="multipart",
            )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PartialKey.objects.count(), 1)
        key: PartialKey = PartialKey.objects.first()
        self.assertEqual(key.capsule, self.capsule)
        self.assertEqual(key.data, self.partial_key_data)

    def test_create_partial_key_for_released_capsule(self):
        url = "/partial-keys/"
        self.create_trustee()
        self.capsule.is_released = True
        self.capsule.save()
        with create_test_data_file(self.partial_key_data) as data_file:
            response = self.client.post(
                self.get_api_url(url),
                {
                    "capsule": reverse("capsule", self.capsule),
                    "data": data_file,
                },
                format="multipart",
            )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(PartialKey.objects.count(), 0)
        self.assertEqual(response.data["capsule"][0].code, "already_released")
