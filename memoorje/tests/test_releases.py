from django.core import mail, management
from django.test import TestCase

from memoorje.crypto import _encrypt_secret
from memoorje.models import Keyslot
from memoorje.tests.mixins import CapsuleReceiverMixin, KeyslotMixin, PartialKeyMixin


class ReleaseTestCase(CapsuleReceiverMixin, KeyslotMixin, PartialKeyMixin, TestCase):
    def test_send_release_notification(self):
        self._create_release_setup()
        mail.outbox.clear()
        management.call_command("releasecapsules")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.capsule_receiver.receiver_token_generator_proxy.make_token(), mail.outbox[0].body)

    def test_send_release_notifications_twice(self):
        self._create_release_setup()
        management.call_command("releasecapsules")
        mail.outbox.clear()
        management.call_command("releasecapsules")
        self.assertEqual(len(mail.outbox), 0)

    def _create_release_setup(self):
        self.create_capsule_receiver()
        self.create_combinable_partial_keys()
        self.create_keyslot(purpose=Keyslot.Purpose.SSS, data=_encrypt_secret(b"capsule secret", self.combined_secret))
