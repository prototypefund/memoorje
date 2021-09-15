from rest_framework import serializers

from memoorje.models import Capsule


class CapsuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Capsule
        fields = ["id"]

    def create(self, validated_data):
        user = self.context["request"].user
        return Capsule.objects.create(owner=user, **validated_data)
