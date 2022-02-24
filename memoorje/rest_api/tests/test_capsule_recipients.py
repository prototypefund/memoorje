from builtins import filter
import json

from django.core import mail
from more_itertools import first
from rest_framework import status

from memoorje.models import CapsuleRecipient
from memoorje.rest_api.tests.utils import MemoorjeAPITestCase, reverse
from memoorje.tests.mixins import CapsuleRecipientMixin


class CapsuleRecipientTestCase(CapsuleRecipientMixin, MemoorjeAPITestCase):
    def test_access_recipients_without_capsule(self):
        """
        Access capsule recipient list without a capsule given.
        """
        url = "/capsule-recipients/"
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.data, [])

    def test_create_capsule_recipient(self):
        """
        Create a recipient for an existing capsule.
        """
        url = "/capsule-recipients/"
        email = "test@example.org"
        self.create_capsule()
        self.authenticate_user()
        response = self.client.post(
            self.get_api_url(url),
            {
                "capsule": reverse("capsule", self.capsule),
                "email": email,
                "name": "Test Name",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CapsuleRecipient.objects.count(), 1)
        capsule_recipient = CapsuleRecipient.objects.get()
        self.assertEqual(capsule_recipient.capsule, self.capsule)
        self.assertEqual(capsule_recipient.email, email)

    def test_create_capsule_recipient_unauthorized(self):
        """
        Create a recipient for a capsule belonging to another user.
        """

        def request(request_url, request_body):
            return self.client.post(self.get_api_url(request_url), request_body)

        url = "/capsule-recipients/"
        self.create_capsule()
        request_data = {
            "capsule": reverse("capsule", self.capsule),
            "email": "test@example.org",
        }
        self.authenticate_user()
        response = request(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.create_user()
        self.authenticate_user()
        response = request(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_capsule_recipients(self):
        """
        List the recipients for a capsule.
        """
        url = "/capsule-recipients/?capsule={pk}"
        self.create_capsule_recipient()
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url, pk=self.capsule.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            json.loads(response.content),
            [
                {
                    "capsule": reverse("capsule", self.capsule, response),
                    "email": self.recipient_email,
                    "id": self.capsule_recipient.id,
                    "isActive": False,
                    "name": "",
                    "url": reverse("capsulerecipient", self.capsule_recipient, response),
                },
            ],
        )

    def test_delete_capsule_recipient(self):
        """
        Delete a capsule recipient.
        """
        url = "/capsule-recipients/{pk}/"
        self.create_capsule_recipient()
        self.authenticate_user()
        response = self.client.delete(self.get_api_url(url, pk=self.capsule_recipient.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CapsuleRecipient.objects.exists())

    def test_recipient_creation_sends_confirmation_request(self):
        """
        An email with a confirmation link should be sent to the capsule recipient.
        """
        self.create_capsule_recipient()
        self.assertGreaterEqual(len(mail.outbox), 1)
        self.assertIn(self.capsule_recipient.email, [m.to[0] for m in mail.outbox])
        msg = first(filter(lambda m: m.to[0] == self.capsule_recipient.email, mail.outbox))
        self.assertIn(self.capsule_recipient.make_confirmation_token(), msg.body)

    def test_confirm_capsule_recipient(self):
        """
        Confirm a capsule recipient's email address.
        """
        url = "/capsule-recipients/{pk}/confirm/"
        self.create_capsule_recipient()
        response = self.client.post(
            self.get_api_url(url, pk=self.capsule_recipient.pk),
            {"token": self.capsule_recipient.make_confirmation_token()},
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.capsule_recipient.refresh_from_db()
        self.assertTrue(self.capsule_recipient.is_email_confirmed)

    def test_confirm_capsule_recipient_twice(self):
        """
        A confirmation token for an email address must not be used twice.
        """
        url = "/capsule-recipients/{pk}/confirm/"
        self.create_capsule_recipient()
        response = self.client.post(
            self.get_api_url(url, pk=self.capsule_recipient.pk),
            {"token": self.capsule_recipient.make_confirmation_token()},
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.post(
            self.get_api_url(url, pk=self.capsule_recipient.pk),
            {"token": self.capsule_recipient.make_confirmation_token()},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirm_other_capsule_recipient(self):
        """
        A confirmation token must not be used for another capsule recipient.
        """
        url = "/capsule-recipients/{pk}/confirm/"
        first = self.create_capsule_recipient()
        second = self.create_capsule_recipient("other@example.org")
        response = self.client.post(
            self.get_api_url(url, pk=first.pk),
            {"token": second.make_confirmation_token()},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_all_capsule_recipients(self):
        """
        List all accessible recipients for a capsule.
        """
        url = "/capsule-recipients/"
        self.create_capsule_recipient()
        self.create_user()
        self.create_capsule_recipient()
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_recipient_name(self):
        url = "/capsule-recipients/{pk}/"
        new_name = "Capsule Recipient New Name"
        self.create_capsule_recipient()
        self.authenticate_user()
        response = self.client.patch(self.get_api_url(url, pk=self.capsule_recipient.pk), {"name": new_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.capsule_recipient.refresh_from_db()
        self.assertEqual(self.capsule_recipient.name, new_name)

    def test_resend_confirmation_email(self):
        url = "/capsule-recipients/{pk}/send-confirmation-email/"
        self.create_capsule_recipient()
        mail.outbox.clear()
        self.authenticate_user()
        response = self.client.post(self.get_api_url(url, pk=self.capsule_recipient.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
