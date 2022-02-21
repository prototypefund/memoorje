from datetime import timedelta

from django.conf import settings
from django.core import mail, management
from django.test import TestCase
from django.utils.timezone import now
from freezegun import freeze_time

from memoorje.tests.mixins import CapsuleRecipientMixin


class JournalTestCase(CapsuleRecipientMixin, TestCase):
    def test_command_sends_no_notification_for_empty_journal(self):
        self._call_command()
        self.assertEqual(len(mail.outbox), 0)

    def test_command_sends_notification_after_recipient_change(self):
        self._change_capsule()
        self._call_command()
        self.assertEqual(len(mail.outbox), 1)

    def test_command_sends_notification_only_once(self):
        self._change_capsule()
        self._call_command()
        self._call_command()
        self.assertEqual(len(mail.outbox), 0)

    def test_command_does_not_send_notifications_before_grace_time(self):
        self._change_capsule(0)
        self._call_command()
        self.assertEqual(len(mail.outbox), 0)

    def _change_capsule(self, time_shift_minutes=settings.JOURNAL_NOTIFICATION_GRACE_PERIOD_MINUTES):
        with freeze_time(now() - timedelta(minutes=time_shift_minutes)):
            self.create_capsule_recipient()

    def _call_command(self):
        mail.outbox.clear()
        management.call_command("sendjournalnotifications")
