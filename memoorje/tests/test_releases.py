from datetime import timedelta

from django.conf import settings
from django.core import mail, management
from django.test import TestCase
from django.utils.timezone import now
from freezegun import freeze_time

from memoorje.crypto import _encrypt_secret
from memoorje.models import Capsule, Keyslot
from memoorje.tests.mixins import CapsuleRecipientMixin, KeyslotMixin, PartialKeyMixin


class ReleaseTestCase(CapsuleRecipientMixin, KeyslotMixin, PartialKeyMixin, TestCase):
    def test_send_release_notification(self):
        self._create_release_setup()
        mail.outbox.clear()
        management.call_command("releasecapsules")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.capsule_recipient.recipient_token_generator_proxy.make_token(), mail.outbox[0].body)
        self.capsule.refresh_from_db()
        self.assertTrue(self.capsule.is_released)

    def test_send_release_notifications_twice(self):
        self._create_release_setup()
        management.call_command("releasecapsules")
        mail.outbox.clear()
        management.call_command("releasecapsules")
        self.assertEqual(len(mail.outbox), 0)

    def test_release_capsules_skips_errors(self):
        self._create_release_setup()
        self.capsule.partial_keys.last().delete()
        mail.outbox.clear()
        management.call_command("releasecapsules")
        self.assertEqual(len(mail.outbox), 0)

    def test_partial_keys_are_deleted_after_release(self):
        self._create_release_setup()
        self.assertEqual(self.capsule.partial_keys.count(), 2)
        management.call_command("releasecapsules")
        self.assertEqual(self.capsule.partial_keys.count(), 0)

    def test_release_two_capsules(self):
        """Release should work as well if more than one capsule exists.

        This is a regression test for #54.
        """
        self._create_release_setup()
        capsule = self.capsule
        self.create_capsule()
        self.assertEqual(Capsule.objects.count(), 2)
        management.call_command("releasecapsules")
        capsule.refresh_from_db()
        self.assertTrue(capsule.is_released)

    def test_release_capsule_immediately(self):
        """Capsules should be released after a grace period is elapsed.

        Regression test for #50.
        """
        self._create_release_setup(0)
        management.call_command("releasecapsules")
        self.capsule.refresh_from_db()
        self.assertFalse(self.capsule.is_released)

    def _create_release_setup(self, time_shift_days=settings.CAPSULE_RELEASE_GRACE_PERIOD_DAYS):
        with freeze_time(now() - timedelta(days=time_shift_days)):
            self.create_capsule_recipient()
            self.create_combinable_partial_keys()
            self.create_keyslot(
                purpose=Keyslot.Purpose.SSS, data=_encrypt_secret(b"capsule secret", self.combined_secret)
            )
