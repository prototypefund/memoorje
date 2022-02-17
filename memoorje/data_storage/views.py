from django.contrib.auth.mixins import UserPassesTestMixin
from django_downloadview import ObjectDownloadView

from memoorje.models import CapsuleContent
from memoorje.utils import get_recipient_by_token


class CapsuleDataDownloadView(UserPassesTestMixin, ObjectDownloadView):
    model = CapsuleContent
    file_field = "data"
    raise_exception = True

    def test_func(self):
        content: CapsuleContent = self.get_object()
        recipient = get_recipient_by_token(self.request)
        return (content.capsule.owner == self.request.user) or (
            recipient is not None and content.capsule.recipients.filter(pk=recipient.pk).exists()
        )
