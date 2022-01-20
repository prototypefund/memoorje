from datetime import timedelta
from decimal import Decimal

from django.core import management
from django.test import TestCase
from rest_framework import status

from memoorje.accounting.models import Transaction
from memoorje.tests.mixins import CapsuleMixin, UserMixin


class AccountingTestCase(CapsuleMixin, TestCase):
    def test_charge_dues(self):
        self.create_capsule()
        self.capsule.created_on -= timedelta(days=40)
        self.capsule.save()
        management.call_command("chargedues")
        self.assertEqual(Transaction.objects.count(), 1)


class APITestCase(UserMixin, TestCase):
    def test_account_balance(self) -> None:
        url = "/api/auth/profile/"
        self.create_transaction(23)
        self.create_transaction(-32)
        self.authenticate_user()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["account_balance"], str(Decimal("-9.00")))

    def create_transaction(self, amount):
        self.ensure_user_exists()
        self.user.transactions.create(amount=amount)
