from rest_framework import serializers
from rest_framework.reverse import reverse

from memoorje import get_authenticated_user
from memoorje.models import Capsule, CapsuleContent


class CapsuleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Capsule
        fields = ["url", "name", "description", "created_on", "updated_on"]

    def create(self, validated_data):
        return Capsule.objects.create(owner=get_authenticated_user(self.context.get("request")), **validated_data)


class CapsuleContentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CapsuleContent
        fields = ["capsule", "metadata", "data"]

    def get_capsule_queryset(self):
        return Capsule.objects.filter(owner=get_authenticated_user(self.context.get("request")))

    def get_extra_kwargs(self):
        kwargs = super().get_extra_kwargs()
        kwargs["capsule"] = {"queryset": self.get_capsule_queryset()}
        return kwargs

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result["data"] = reverse("capsule-content-data", args=[instance.pk], request=self.context["request"])
        return result
