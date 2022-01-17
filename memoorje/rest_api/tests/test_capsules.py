import json

from rest_framework import status

from memoorje.models import Capsule, CapsuleReceiver, Keyslot, PartialKey, Trustee
from memoorje.rest_api.tests.utils import format_time, MemoorjeAPITestCase, reverse
from memoorje.tests.mixins import CapsuleMixin, CapsuleReceiverMixin, KeyslotMixin, PartialKeyMixin, TrusteeMixin


class CapsuleTestCase(CapsuleMixin, MemoorjeAPITestCase):
    def test_create_capsule_unauthorized(self) -> None:
        """Create a capsule unauthorized."""
        url = "/capsules/"
        response = self.client.post(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_capsule(self) -> None:
        """Create a capsule."""
        url = "/capsules/"
        self.authenticate_user()
        response = self.client.post(self.get_api_url(url), data={"name": "test", "description": "test"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Capsule.objects.count(), 1)
        self.assertEqual(Capsule.objects.get().owner, self.user)

    def test_retrieve_capsule_unauthorized(self) -> None:
        """Retrieve a capsule unauthorized."""
        url = "/capsules/{id}/"
        self.create_capsule()
        response = self.client.post(self.get_api_url(url, id=self.capsule.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_capsule(self) -> None:
        """Retrieve a capsule."""
        url = "/capsules/{id}/"
        self.create_capsule()
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url, id=self.capsule.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "createdOn": format_time(self.capsule.created_on),
                "description": self.capsule_description,
                "id": str(self.capsule.id),
                "name": self.capsule_name,
                "updatedOn": format_time(self.capsule.updated_on),
                "url": reverse("capsule", self.capsule, response),
            },
        )

    def test_retrieve_others_capsule(self) -> None:
        """Retrieve a capsule which does not belong to the logged in user."""
        url = "/capsules/{pk}/"
        other_capsule = self.create_capsule()
        self.create_user()
        self.create_capsule()
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url, pk=other_capsule.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_capsule(self) -> None:
        """Update a capsule's name and description."""
        url = "/capsules/{pk}/"
        new_name = "Changed name"
        new_description = "Changed description"
        self.create_capsule()
        self.authenticate_user()
        response = self.client.put(
            self.get_api_url(url, pk=self.capsule.pk),
            {
                "name": new_name,
                "description": new_description,
            },
        )
        self.capsule.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(new_name, self.capsule.name)
        self.assertEqual(new_description, self.capsule.description)

    def test_list_capsules(self):
        """List a user's capsules."""
        url = "/capsules/"
        self.create_capsule()
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            json.loads(response.content),
            [
                {
                    "createdOn": format_time(self.capsule.created_on),
                    "description": self.capsule_description,
                    "id": str(self.capsule.id),
                    "name": self.capsule_name,
                    "updatedOn": format_time(self.capsule.updated_on),
                    "url": reverse("capsule", self.capsule, response),
                },
            ],
        )

    def test_delete_capsule(self):
        """Delete a capsule."""
        url = "/capsules/{pk}/"
        self.create_capsule()
        self.authenticate_user()
        response = self.client.delete(self.get_api_url(url, pk=self.capsule.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Capsule.objects.exists())

    def test_list_all_capsules(self):
        """
        List all accessible capsules.
        """
        url = "/capsules/"
        self.create_capsule()
        self.create_user()
        self.create_capsule()
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class CapsuleAccessWithReceiverTokenTestCase(CapsuleReceiverMixin, MemoorjeAPITestCase):
    def test_retrieve_capsule(self):
        """Gain access to a capsule by providing a receiver token."""
        url = "/capsules/{pk}/"
        self.create_capsule_receiver()
        response = self.client.get(
            self.get_api_url(url, pk=self.capsule.pk),
            **self.get_request_headers(with_receiver_token_for=self.capsule_receiver),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_capsules(self):
        """List capsule(s) for the given receiver."""
        url = "/capsules/"
        self.create_capsule_receiver()
        response = self.client.get(
            self.get_api_url(url), **self.get_request_headers(with_receiver_token_for=self.capsule_receiver)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_capsule(self) -> None:
        """Creating a capsule is forbidden if not authenticated."""
        url = "/capsules/"
        self.create_capsule_receiver()
        response = self.client.post(
            self.get_api_url(url), **self.get_request_headers(with_receiver_token_for=self.capsule_receiver)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_capsule(self) -> None:
        """Updating a capsule is forbidden if not authenticated."""
        url = "/capsules/{pk}/"
        self.create_capsule_receiver()
        response = self.client.put(
            self.get_api_url(url, pk=self.capsule.pk),
            **self.get_request_headers(with_receiver_token_for=self.capsule_receiver),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_capsule(self):
        """Deleting a capsule is forbidden if not authenticated."""
        url = "/capsules/{pk}/"
        self.create_capsule_receiver()
        response = self.client.delete(
            self.get_api_url(url, pk=self.capsule.pk),
            **self.get_request_headers(with_receiver_token_for=self.capsule_receiver),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AuthenticatedCapsuleAccessWithReceiverTokenTestCase(CapsuleReceiverMixin, MemoorjeAPITestCase):
    def test_retrieve_capsule(self):
        """Gain access to capsules by providing auth and a receiver token."""
        url = "/capsules/{pk}/"
        receiver = self._create_two_capsules_and_authenticate()
        response = self.client.get(
            self.get_api_url(url, pk=self.capsule.pk), **self.get_request_headers(with_receiver_token_for=receiver)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(
            self.get_api_url(url, pk=receiver.capsule.pk), **self.get_request_headers(with_receiver_token_for=receiver)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_capsules_without_token(self):
        """List capsule(s) for the given receiver without a receiver token."""
        response = self._list_capsules(with_token=False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_capsules(self):
        """List capsule(s) for the given receiver."""
        response = self._list_capsules(with_token=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_capsule(self) -> None:
        """You can still create capsules, even if you supply a token."""
        url = "/capsules/"
        self.create_capsule_receiver()
        self.authenticate_user()
        response = self.client.post(
            self.get_api_url(url),
            data={"name": "test", "description": "test"},
            **self.get_request_headers(with_receiver_token_for=self.capsule_receiver),
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_own_capsule(self):
        """You can delete your own capsules."""
        url = "/capsules/{pk}/"
        receiver = self._create_two_capsules_and_authenticate()
        response = self.client.delete(
            self.get_api_url(url, pk=self.capsule.pk),
            **self.get_request_headers(with_receiver_token_for=receiver),
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_receiver_capsule(self):
        """You must not delete a received capsule."""
        url = "/capsules/{pk}/"
        receiver = self._create_two_capsules_and_authenticate()
        response = self.client.delete(
            self.get_api_url(url, pk=receiver.capsule.pk),
            **self.get_request_headers(with_receiver_token_for=receiver),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _create_two_capsules_and_authenticate(self) -> CapsuleReceiver:
        receiver = self.create_capsule_receiver()
        self.create_user()
        self.create_capsule()
        self.authenticate_user()
        return receiver

    def _list_capsules(self, with_token: bool):
        url = "/capsules/"
        receiver = self._create_two_capsules_and_authenticate()
        headers = {"with_receiver_token_for": receiver} if with_token else {}
        return self.client.get(self.get_api_url(url), **self.get_request_headers(**headers))


class AbortTestCase(KeyslotMixin, PartialKeyMixin, TrusteeMixin, MemoorjeAPITestCase):
    def test_abort_removes_partial_keys(self):
        """Aborting a release process removes all partial keys."""
        url = "/capsules/{pk}/abort-release/"
        self.create_partial_key()
        self.authenticate_user()
        response = self.client.post(self.get_api_url(url, pk=self.capsule.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(PartialKey.objects.exists())

    def test_abort_unaccidental_release_removes_keyslot_and_trustees(self):
        """Aborting a release process, which was not accidentally initiated, removes the keyslot and all trustees."""
        url = "/capsules/{pk}/abort-release/"
        self.create_keyslot(purpose=Keyslot.Purpose.SSS)
        self.create_partial_key()
        self.create_trustee()
        self.authenticate_user()
        response = self.client.post(self.get_api_url(url, pk=self.capsule.pk), {"is_accidental": False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Keyslot.objects.exists())
        self.assertFalse(PartialKey.objects.exists())
        self.assertFalse(Trustee.objects.exists())
