from rest_framework import status

from memoorje.models import CapsuleContent
from memoorje.rest_api.tests import MemoorjeAPITestCase
from memoorje.rest_api.tests.capsules import CapsuleMixin


class CapsuleContentMixin(CapsuleMixin):
    def create_capsule_content(self):
        return CapsuleContent.objects.create(capsule=self.capsule)


class CapsuleContentTestCase(CapsuleContentMixin, MemoorjeAPITestCase):
    def test_access_contents_without_capsule(self):
        """
        Access capsule content list without a capsule given
        """
        url = "/capsule-contents/"
        self.authenticate_user()
        response = self.client.get(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.post(self.get_api_url(url))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_capsule_content(self):
        """
        Create a content for an existing capsule
        """
        url = "/capsule-contents/?capsule={pk}"
        self.create_capsule()
        self.authenticate_user()
        response = self.client.post(self.get_api_url(url, pk=self.capsule.pk))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CapsuleContent.objects.count(), 1)
        self.assertEqual(CapsuleContent.objects.get().capsule, self.capsule)

    def test_modify_capsule(self):
        """
        Any capsule and capsule content modifications should update the capsule's update timestamp.
        """
        self.create_capsule()

        # change an attribute of the capsule itself
        initial_updated_on = self.capsule.updated_on
        # TODO: we might want to change this to an API request
        self.capsule.name = "Changed the name"
        self.capsule.save()
        self.assertGreater(self.capsule.updated_on, initial_updated_on)

        # modify capsule's content
        initial_updated_on = self.capsule.updated_on
        content = self.create_capsule_content()
        self.assertGreater(self.capsule.updated_on, initial_updated_on)
        initial_updated_on = self.capsule.updated_on
        content.delete()
        self.assertGreater(self.capsule.updated_on, initial_updated_on)
