from rest_framework import serializers

from memoorje import get_authenticated_user
from memoorje.models import Capsule, CapsuleContent, CapsuleReceiver
from memoorje.rest_api.fields import BinaryField


class CapsuleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Capsule
        fields = ["created_on", "description", "id", "name", "updated_on", "url"]

    def create(self, validated_data):
        return Capsule.objects.create(owner=get_authenticated_user(self.context.get("request")), **validated_data)


class CapsuleContentSerializer(serializers.HyperlinkedModelSerializer):
    metadata = BinaryField()

    class Meta:
        model = CapsuleContent
        fields = ["capsule", "data", "id", "metadata", "url"]

    def get_capsule_queryset(self):
        return Capsule.objects.filter(owner=get_authenticated_user(self.context.get("request")))

    def get_extra_kwargs(self):
        kwargs = super().get_extra_kwargs()
        kwargs["capsule"] = {"queryset": self.get_capsule_queryset()}
        return kwargs


class CapsuleReceiverSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CapsuleReceiver
        fields = ["capsule", "email", "id", "url"]

    def get_capsule_queryset(self):
        return Capsule.objects.filter(owner=get_authenticated_user(self.context.get("request")))

    def get_extra_kwargs(self):
        kwargs = super().get_extra_kwargs()
        kwargs["capsule"] = {"queryset": self.get_capsule_queryset()}
        return kwargs
