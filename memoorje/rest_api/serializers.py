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

    def get_capsule_queryset(self):
        user = self.context["request"].user
        return Capsule.objects.filter(owner=user)

    def get_extra_kwargs(self):
        kwargs = super().get_extra_kwargs()
        kwargs["capsule"] = {"queryset": self.get_capsule_queryset()}
        return kwargs

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result["data"] = reverse("capsule-content-data", args=[instance.pk], request=self.context["request"])
        return result
