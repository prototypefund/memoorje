from rest_framework import serializers

from memoorje.accounting.models import Transaction


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Transaction
        fields = ["amount", "created_on", "id", "type"]
