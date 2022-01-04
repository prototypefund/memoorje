from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core import mail, management
from django.test import TestCase

from memoorje.tests.mixins import CapsuleReceiverMixin


class CapsuleHintTestCase(CapsuleReceiverMixin, TestCase):
    def test_no_hints_sent_to_newly_created_capsule_owner(self):
        self.create_capsule_receiver()
        mail.outbox.clear()
        management.call_command("sendcapsulehints")
        self.assertEqual(len(mail.outbox), 0)

    def test_hints_sent_to_capsule_owner_with_old_inactive_receiver(self):
        self.create_capsule_receiver()
        self.capsule_receiver.created_on -= relativedelta(days=settings.INACTIVE_RECEIVER_HINT_DAYS)
        self.capsule_receiver.save()
        mail.outbox.clear()
        management.call_command("sendcapsulehints")
        self.assertEqual(len(mail.outbox), 1)
