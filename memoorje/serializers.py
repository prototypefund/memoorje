from rest_framework import serializers

from memoorje.models import Capsule


class CapsuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Capsule
        fields = ["id"]
