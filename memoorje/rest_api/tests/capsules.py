import json

from rest_framework import status
from rest_framework.reverse import reverse

from memoorje.models import Capsule
from memoorje.rest_api.tests import MemoorjeAPITestCase
from memoorje.rest_api.tests.auth import UserMixin


class CapsuleMixin(UserMixin):
    capsule: Capsule
    capsule_description: str
    capsule_name: str

    def create_capsule(self) -> Capsule:
        self.ensure_user_exists()
        self.capsule_name = "test"
        self.capsule_description = "test"
        self.capsule = Capsule.objects.create(
            owner=self.user, name=self.capsule_name, description=self.capsule_description
        )
        return self.capsule


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
                "url": reverse("capsule-detail", args=[self.capsule.pk], request=response.wsgi_request),
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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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
