from datetime import date

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core import mail, management
from django.test import TestCase

from memoorje.tests.mixins import CapsuleMixin


class ReminderTestCase(CapsuleMixin, TestCase):
    def test_user_without_capsule(self):
        self.create_user()
        management.call_command("sendreminders")
        self.assertEqual(len(mail.outbox), 0)

    def test_user_with_capsule(self):
        self.create_capsule()
        management.call_command("sendreminders")
        self.assertEqual(len(mail.outbox), 0)

    def test_user_with_old_capsule(self):
        self.create_capsule()
        self.capsule.created_on -= relativedelta(months=settings.DEFAULT_REMIND_INTERVAL + 1)
        self.capsule.save()
        management.call_command("sendreminders")
        self.assertEqual(len(mail.outbox), 1)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.last_reminder_sent_on)

    def test_user_with_old_reminder(self):
        self.create_capsule()
        old_reminder_date = date.today() - relativedelta(months=settings.DEFAULT_REMIND_INTERVAL + 1)
        self.user.last_reminder_sent_on = old_reminder_date
        self.user.save()
        management.call_command("sendreminders")
        self.assertEqual(len(mail.outbox), 1)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.last_reminder_sent_on, old_reminder_date)

    def test_user_with_reminder_just_sent(self):
        self.create_capsule()
        self.user.last_reminder_sent_on = date.today()
        self.user.save()
        management.call_command("sendreminders")
        self.assertEqual(len(mail.outbox), 0)
