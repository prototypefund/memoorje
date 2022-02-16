import json

from rest_framework import status

from memoorje.models import PartialKey, Trustee
from memoorje.rest_api.tests.utils import MemoorjeAPITestCase, reverse
from memoorje.tests.mixins import CapsuleRecipientMixin, TrusteeMixin


class TrusteeTestCase(TrusteeMixin, MemoorjeAPITestCase):
    def test_access_trustees_without_capsule(self):
        """Access trustee list without a capsule given"""
        url = "/trustees/"
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.data, [])

    def test_create_trustee(self):
        """Create a trustee for an existing capsule"""
        url = "/trustees/"
        email = "trustee@example.org"
        self.create_capsule()
        self.authenticate_user()
        response = self.client.post(
            self.get_api_url(url),
            {
                "capsule": reverse("capsule", self.capsule),
                "email": email,
                "partialKeySha256": PartialKey.hash_key_data(b"Test Data").hex(),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Trustee.objects.count(), 1)
        trustee = Trustee.objects.get()
        self.assertEqual(trustee.capsule, self.capsule)
        self.assertEqual(trustee.email, email)

    def test_create_trustee_unauthorized(self):
        """Create a trustee for a capsule belonging to another user."""
        url = "/trustees/"
        # create a capsule (and an user)
        self.create_capsule()
        # create another user
        self.create_user()
        self.authenticate_user()
        response = self.client.post(
            self.get_api_url(url),
            {
                "capsule": reverse("capsule", self.capsule),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["capsule"][0].code, "does_not_exist")

    def test_list_trustees(self):
        """List the trustees for a capsule."""
        url = "/trustees/?capsule={pk}"
        self.create_trustee()
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url, pk=self.capsule.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            json.loads(response.content),
            [
                {
                    "capsule": reverse("capsule", self.capsule, response),
                    "id": self.trustee.id,
                    "email": self.trustee_email,
                    "name": "",
                    "url": reverse("trustee", self.trustee, response),
                },
            ],
        )

    def test_delete_trustee(self):
        """Delete a trustee."""
        url = "/trustees/{pk}/"
        self.create_trustee()
        self.authenticate_user()
        response = self.client.delete(self.get_api_url(url, pk=self.trustee.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Trustee.objects.exists())

    def test_list_all_trustees(self):
        """
        List all accessible trustees for a capsule.
        """
        url = "/trustees/"
        self.create_trustee()
        self.create_user()
        self.create_trustee()
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class AuthenticatedTrusteeAccessWithRecipientTokenTestCase(CapsuleRecipientMixin, TrusteeMixin, MemoorjeAPITestCase):
    def test_list_trustees(self):
        """List trustee(s) for the given recipient."""
        url = "/trustees/"
        recipient = self.create_capsule_recipient()
        self.create_trustee()
        self.create_user()
        self.create_trustee()
        self.authenticate_user()
        response = self.client.get(
            self.get_api_url(url), **self.get_request_headers(with_recipient_token_for=recipient)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(self.user, recipient)
        self.assertEqual(Trustee.objects.count(), 2)
        self.assertEqual(len(response.data), 1)
