import json

from rest_framework import status

from memoorje.models import Capsule
from memoorje.rest_api.tests import MemoorjeAPITestCase
from memoorje.tests import CapsuleMixin


class CapsuleTestCase(CapsuleMixin, MemoorjeAPITestCase):
    def test_create_capsule_unauthorized(self) -> None:
        """
        Create a capsule unauthorized
        """
        url = "/capsules/"
        response = self.client.post(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_capsule(self) -> None:
        """
        Create a capsule
        """
        url = "/capsules/"
        self.authenticate_user()
        response = self.client.post(self.get_api_url(url), data={"name": "test", "description": "test"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Capsule.objects.count(), 1)
        self.assertEqual(Capsule.objects.get().owner, self.user)

    def test_retrieve_capsule_unauthorized(self) -> None:
        """
        Retrieve a capsule unauthorized
        """
        url = "/capsules/{id}/"
        self.create_capsule()
        response = self.client.post(self.get_api_url(url, id=self.capsule.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_capsule(self) -> None:
        """
        Retrieve a capsule
        """
        url = "/capsules/{id}/"
        self.create_capsule()
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url, id=self.capsule.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "url": self.get_capsule_url(response=response),
                "createdOn": self.capsule.created_on.isoformat()[:-6] + "Z",
                "updatedOn": self.capsule.updated_on.isoformat()[:-6] + "Z",
                "name": self.capsule_name,
                "description": self.capsule_description,
            },
        )

    def test_retrieve_others_capsule(self) -> None:
        """
        Retrieve a capsule which does not belong to the logged in user
        """
        url = "/capsules/{pk}/"
        other_capsule = self.create_capsule()
        self.create_user()
        self.create_capsule()
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url, pk=other_capsule.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_capsule(self) -> None:
        """
        Update a capsule's name and description.
        """
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
        """
        List a user's capsules.
        """
        url = "/capsules/"
        self.create_capsule()
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            json.loads(response.content),
            [
                {
                    "url": self.get_capsule_url(response=response),
                    "createdOn": self.capsule.created_on.isoformat()[:-6] + "Z",
                    "updatedOn": self.capsule.updated_on.isoformat()[:-6] + "Z",
                    "name": self.capsule_name,
                    "description": self.capsule_description,
                },
            ],
        )

    def test_delete_capsule(self):
        """
        Delete a capsule.
        """
        url = "/capsules/{pk}/"
        self.create_capsule()
        self.authenticate_user()
        response = self.client.delete(self.get_api_url(url, pk=self.capsule.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Capsule.objects.exists())
