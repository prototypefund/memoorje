from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.utils.timezone import now


class CurrencyField(models.DecimalField):
    def __init__(self, **kwargs):
        kwargs.update(settings.CURRENCY_REPRESENTATION)
        super().__init__(**kwargs)


class ExpenseType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ExpenseQuerySet(models.QuerySet):
    def get_amount_sum(self):
        reference_period = relativedelta(months=settings.EXPENSE_TYPE_AMOUNT_SUM_REFERENCE_PERIOD_MONTHS)
        amount_sum = self.filter(created_on__gt=now() - reference_period).aggregate(Sum("amount"))
        return amount_sum["amount__sum"] or Decimal(0)


class Expense(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    creator_name = models.CharField(max_length=100)
    type = models.ForeignKey("ExpenseType", on_delete=models.SET_NULL, null=True, related_name="expenses")
    description = models.CharField(max_length=255)
    amount = CurrencyField()

    objects = models.Manager.from_queryset(ExpenseQuerySet)()


class TransactionManager(models.Manager):
    def get_balance(self):
        return self.get_queryset().aggregate(Sum("amount"))["amount__sum"] or Decimal(0)


class Transaction(models.Model):
    class Type(models.TextChoices):
        MONTHLY_DUE = "DU"
        CREDIT = "CR"
        REFUND = "RF"

    # (internal) timestamp
    created_on = models.DateTimeField(auto_now_add=True)
    # a possible external timestamp, like a booking date on a bank account
    booked_on = models.DateTimeField(null=True)
    # all transactions are related to exactly one user
    account_holder = models.ForeignKey("memoorje.User", on_delete=models.CASCADE, related_name="transactions")
    # a transaction *might* be related to a capsule
    capsule = models.ForeignKey(
        "memoorje.Capsule", on_delete=models.SET_NULL, null=True, blank=True, related_name="transactions"
    )
    # internal transactions don't have a corresponding transaction on a bank account
    type = models.CharField(max_length=2, choices=Type.choices)
    # external bank transactions might supply a name for reference
    external_name = models.CharField(max_length=100)
    # description, purpose, subject or any other notes
    description = models.CharField(max_length=255)
    # the actual amount (positive = incoming)
    amount = CurrencyField()

    objects = TransactionManager()
