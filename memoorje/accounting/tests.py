from datetime import timedelta

from django.core import management
from django.test import TestCase

from memoorje.accounting.models import Transaction
from memoorje.tests.mixins import CapsuleMixin


class AccountingTestCase(CapsuleMixin, TestCase):
    def test_charge_dues(self):
        self.create_capsule()
        self.capsule.created_on -= timedelta(days=40)
        self.capsule.save()
        management.call_command("chargedues")
        self.assertEqual(Transaction.objects.count(), 1)
