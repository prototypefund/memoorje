from rest_framework import mixins, viewsets

from memoorje.accounting.models import ExpenseType
from memoorje.accounting.serializers import ExpenseTypeSerializer, TransactionSerializer


class ExpenseTypeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = ExpenseType.objects
    serializer_class = ExpenseTypeSerializer


class TransactionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return self.request.user.transactions.order_by("created_on")
