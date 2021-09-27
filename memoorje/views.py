from django.contrib.auth.mixins import UserPassesTestMixin
from django_downloadview import ObjectDownloadView

from memoorje.models import CapsuleContent


class CapsuleContentDataDownloadView(UserPassesTestMixin, ObjectDownloadView):
    model = CapsuleContent
    file_field = "data"
    raise_exception = True

    def test_func(self):
        content: CapsuleContent = self.get_object()
        return content.capsule.owner == self.request.user
