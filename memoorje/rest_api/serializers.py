from rest_framework import serializers

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
        fields = ["capsule", "metadata"]

    def validate_capsule(self, value: Capsule) -> Capsule:
        if value.owner != self.context["request"].user:
            raise serializers.ValidationError("You may not access capsule's content")
        return value

    def create(self, validated_data):
        return CapsuleContent.objects.create(**validated_data)
