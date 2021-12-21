from django.core import mail, management
from django.test import TestCase

from memoorje.tests.mixins import CapsuleReceiverMixin, PartialKeyMixin


class ReleaseTestCase(CapsuleReceiverMixin, PartialKeyMixin, TestCase):
    def test_send_release_notification(self):
        self.create_capsule_receiver()
        self.create_partial_key()
        mail.outbox.clear()
        management.call_command("releasecapsules")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.capsule_receiver.receiver_token_generator_proxy.make_token(), mail.outbox[0].body)

    def test_send_release_notifications_twice(self):
        self.create_capsule_receiver()
        self.create_partial_key()
        management.call_command("releasecapsules")
        mail.outbox.clear()
        management.call_command("releasecapsules")
        self.assertEqual(len(mail.outbox), 0)
