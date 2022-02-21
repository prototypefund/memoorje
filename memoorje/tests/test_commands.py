from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core import mail, management
from django.test import TestCase

from memoorje.tests.mixins import CapsuleRecipientMixin, PartialKeyMixin, TrusteeMixin


class HintTestCase(CapsuleRecipientMixin, TestCase):
    def test_no_hints_sent_to_newly_created_capsule_owner(self):
        self.create_capsule_recipient()
        mail.outbox.clear()
        management.call_command("sendcapsulehints")
        self.assertEqual(len(mail.outbox), 0)

    def test_hints_sent_to_capsule_owner_with_old_inactive_recipient(self):
        self.create_capsule_recipient()
        self.capsule_recipient.created_on -= relativedelta(days=settings.INACTIVE_RECIPIENT_HINT_DAYS)
        self.capsule_recipient.save()
        mail.outbox.clear()
        management.call_command("sendcapsulehints")
        self.assertEqual(len(mail.outbox), 1)


class InvitationTestCase(PartialKeyMixin, TrusteeMixin, TestCase):
    def test_invitations_sent_to_trustees(self):
        self.create_trustee()
        self.create_trustee()
        self.create_partial_key()
        self.partial_key.created_on -= relativedelta(days=settings.CAPSULE_RELEASE_GRACE_PERIOD_DAYS)
        self.partial_key.save()
        mail.outbox.clear()
        management.call_command("sendpartialkeyinvitations")
        self.assertEqual(len(mail.outbox), 2)
        for m in mail.outbox:
            self.assertIn(self.capsule.name, m.body)
            self.assertIn(self.capsule.description, m.body)
            self.assertIn(str(self.capsule.pk), m.body)
