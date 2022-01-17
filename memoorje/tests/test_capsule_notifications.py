from django.core import mail
from django.test import TestCase

from memoorje.models import PartialKey
from memoorje.tests.mixins import CapsuleRecipientMixin, TrusteeMixin


class CapsuleNotificationTestCase(CapsuleRecipientMixin, TrusteeMixin, TestCase):
    def test_create_recipient_sends_notification(self):
        self.create_capsule()
        mail.outbox.clear()
        self.create_capsule_recipient()
        self.assertGreaterEqual(len(mail.outbox), 1)
        self.assertIn("Recipients of your capsule have changed", "".join([m.body for m in mail.outbox]))

    def test_create_partial_key_sends_notification(self):
        self.create_trustee()
        mail.outbox.clear()
        PartialKey.objects.create(capsule=self.capsule, data=self.partial_key_data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Release of the capsule has been initiated", mail.outbox[0].body)
