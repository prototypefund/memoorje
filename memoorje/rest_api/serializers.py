from rest_framework import serializers
from rest_framework.reverse import reverse

from memoorje.models import Capsule, CapsuleContent


class CapsuleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Capsule
        fields = ["url", "name", "description", "created_on", "updated_on"]

    def create(self, validated_data):
        user = self.context["request"].user
        return Capsule.objects.create(owner=user, **validated_data)


class CapsuleContentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CapsuleContent
        fields = ["capsule", "metadata", "data"]

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result["data"] = reverse("capsule-content-data", args=[instance.pk], request=self.context["request"])
        return result

    def validate_capsule(self, value: Capsule) -> Capsule:
        if value.owner != self.context["request"].user:
            raise serializers.ValidationError("You may not access capsule's content")
        return value
