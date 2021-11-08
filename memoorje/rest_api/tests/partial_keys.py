from rest_framework import status

from memoorje.rest_api.tests.memoorje import get_url, MemoorjeAPITestCase
from memoorje.tests.memoorje import create_test_data_file
from memoorje.tests.mixins import CapsuleMixin


class PartialKeyTestCase(CapsuleMixin, MemoorjeAPITestCase):
    def test_create_partial_key(self):
        url = "/partial-keys/"
        data = b"Partial key data according to Shamir's Secret Sharing Scheme"
        self.create_capsule()
        with create_test_data_file(data) as data_file:
            response = self.client.post(
                self.get_api_url(url),
                {
                    "capsule": get_url("capsule", self.capsule),
                    "data": data_file,
                },
                format="multipart",
            )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
