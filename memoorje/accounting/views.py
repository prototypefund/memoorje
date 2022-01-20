from rest_framework import viewsets

from memoorje.accounting.serializers import TransactionSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return self.request.user.transactions.order_by("created_on")
