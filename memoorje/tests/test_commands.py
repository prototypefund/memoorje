from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core import mail, management
from django.test import TestCase

from memoorje.tests.mixins import CapsuleReceiverMixin, PartialKeyMixin, TrusteeMixin


class HintTestCase(CapsuleReceiverMixin, TestCase):
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


class InvitationTestCase(PartialKeyMixin, TrusteeMixin, TestCase):
    def test_invitations_sent_to_trustees(self):
        self.create_trustee()
        self.create_trustee()
        self.create_partial_key()
        self.partial_key.created_on -= relativedelta(days=settings.TRUSTEE_PARTIAL_KEY_INVITATION_GRACE_PERIOD_DAYS)
        self.partial_key.save()
        mail.outbox.clear()
        management.call_command("sendpartialkeyinvitations")
        self.assertEqual(len(mail.outbox), 2)