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
        fields = ["metadata"]

    def create(self, validated_data):
        capsule = self.context["request"].capsule
        return CapsuleContent.objects.create(capsule=capsule, **validated_data)
