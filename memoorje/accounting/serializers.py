from django.conf import settings
from rest_framework import serializers

from memoorje.accounting.models import Expense, ExpenseType, Transaction
from memoorje.models import Capsule


class ExpenseTypeListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        result = super().to_representation(data)
        result.append(ExpenseTypeSerializer().to_representation(ExpenseType(name=None)))
        return result


class ExpenseTypeSerializer(serializers.HyperlinkedModelSerializer):
    amount_sum_per_capsule = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ExpenseType
        fields = ["amount_sum_per_capsule", "name"]
        list_serializer_class = ExpenseTypeListSerializer

    def get_amount_sum_per_capsule(self, obj):
        amount_sum = self._get_expense_query_set(obj).get_amount_sum()
        capsule_count = Capsule.objects.count()
        # FIXME: this will fail if there are no capsules
        result = amount_sum / capsule_count
        return serializers.DecimalField(**settings.CURRENCY_REPRESENTATION).to_representation(result)

    def _get_expense_query_set(self, expense_type: ExpenseType):
        if expense_type.name is None:
            return Expense.objects.filter(type__isnull=True)
        return expense_type.expenses


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Transaction
        fields = ["amount", "created_on", "id", "type"]
