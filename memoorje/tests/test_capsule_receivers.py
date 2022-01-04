from django.core import mail
from django.test import TestCase

from memoorje.tests.mixins import CapsuleReceiverMixin


class CapsuleReceiverTestCase(CapsuleReceiverMixin, TestCase):
    def test_create_receiver_sends_notification(self):
        self.create_capsule()
        mail.outbox.clear()
        self.create_capsule_receiver()
        self.assertGreaterEqual(len(mail.outbox), 1)
        self.assertIn("Recipients of your capsule have changed", "".join([m.body for m in mail.outbox]))
