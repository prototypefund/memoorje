import json

from django.core import mail
from rest_framework import status

from memoorje.models import CapsuleReceiver
from memoorje.rest_api.tests.memoorje import get_url, MemoorjeAPITestCase
from memoorje.tests.mixins import CapsuleReceiverMixin


class CapsuleReceiverTestCase(CapsuleReceiverMixin, MemoorjeAPITestCase):
    def test_access_receivers_without_capsule(self):
        """
        Access capsule receiver list without a capsule given.
        """
        url = "/capsule-receivers/"
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.data, [])

    def test_create_capsule_receiver(self):
        """
        Create a receiver for an existing capsule.
        """
        url = "/capsule-receivers/"
        email = "test@example.org"
        self.create_capsule()
        self.authenticate_user()
        response = self.client.post(
            self.get_api_url(url),
            {
                "capsule": get_url("capsule", self.capsule),
                "email": email,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CapsuleReceiver.objects.count(), 1)
        capsule_receiver = CapsuleReceiver.objects.get()
        self.assertEqual(capsule_receiver.capsule, self.capsule)
        self.assertEqual(capsule_receiver.email, email)

    def test_create_capsule_receiver_unauthorized(self):
        """
        Create a receiver for a capsule belonging to another user.
        """

        def request(request_url, request_body):
            return self.client.post(self.get_api_url(request_url), request_body)

        url = "/capsule-receivers/"
        self.create_capsule()
        request_data = {
            "capsule": get_url("capsule", self.capsule),
            "email": "test@example.org",
        }
        self.authenticate_user()
        response = request(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.create_user()
        self.authenticate_user()
        response = request(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_capsule_receivers(self):
        """
        List the receivers for a capsule.
        """
        url = "/capsule-receivers/?capsule={pk}"
        self.create_capsule_receiver()
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url, pk=self.capsule.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            json.loads(response.content),
            [
                {
                    "capsule": get_url("capsule", self.capsule, response),
                    "email": self.receiver_email,
                    "id": self.capsule_receiver.id,
                    "isActive": False,
                    "url": get_url("capsulereceiver", self.capsule_receiver, response),
                },
            ],
        )

    def test_delete_capsule_receiver(self):
        """
        Delete a capsule receiver.
        """
        url = "/capsule-receivers/{pk}/"
        self.create_capsule_receiver()
        self.authenticate_user()
        response = self.client.delete(self.get_api_url(url, pk=self.capsule_receiver.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CapsuleReceiver.objects.exists())

    def test_receiver_creation_sends_confirmation_request(self):
        """
        An email with a confirmation link should be sent to the capsule receiver.
        """
        self.create_capsule_receiver()
        self.assertGreaterEqual(len(mail.outbox), 1)
        self.assertIn(self.capsule_receiver.make_confirmation_token(), "".join([m.body for m in mail.outbox]))

    def test_confirm_capsule_receiver(self):
        """
        Confirm a capsule receivers email address.
        """
        url = "/capsule-receivers/{pk}/confirm/"
        self.create_capsule_receiver()
        response = self.client.post(
            self.get_api_url(url, pk=self.capsule_receiver.pk),
            {"token": self.capsule_receiver.make_confirmation_token()},
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.capsule_receiver.refresh_from_db()
        self.assertTrue(self.capsule_receiver.is_email_confirmed)

    def test_confirm_capsule_receiver_twice(self):
        """
        A confirmation token for an email address must not be used twice.
        """
        url = "/capsule-receivers/{pk}/confirm/"
        self.create_capsule_receiver()
        response = self.client.post(
            self.get_api_url(url, pk=self.capsule_receiver.pk),
            {"token": self.capsule_receiver.make_confirmation_token()},
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.post(
            self.get_api_url(url, pk=self.capsule_receiver.pk),
            {"token": self.capsule_receiver.make_confirmation_token()},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirm_other_capsule_receiver(self):
        """
        A confirmation token must not be used for another capsule receiver.
        """
        url = "/capsule-receivers/{pk}/confirm/"
        first = self.create_capsule_receiver()
        second = self.create_capsule_receiver("other@example.org")
        response = self.client.post(
            self.get_api_url(url, pk=first.pk),
            {"token": second.make_confirmation_token()},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_all_capsule_receivers(self):
        """
        List all accessible receivers for a capsule.
        """
        url = "/capsule-receivers/"
        self.create_capsule_receiver()
        self.create_user()
        self.create_capsule_receiver()
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
