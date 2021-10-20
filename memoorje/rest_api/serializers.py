from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from memoorje import get_authenticated_user
from memoorje.models import Capsule, CapsuleContent, CapsuleReceiver
from memoorje.rest_api.fields import BinaryField


class CapsuleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Capsule
        fields = ["created_on", "description", "id", "name", "updated_on", "url"]

    def create(self, validated_data):
        return Capsule.objects.create(owner=get_authenticated_user(self.context.get("request")), **validated_data)


class CapsuleRelatedSerializerMixin:
    """
    Restricts the queryset for the `capsule` field of the serializer to capsules of the current user.
    """

    def get_capsule_queryset(self):
        return Capsule.objects.filter(owner=get_authenticated_user(self.context.get("request")))

    def get_extra_kwargs(self):
        kwargs = super().get_extra_kwargs()
        kwargs["capsule"] = {"queryset": self.get_capsule_queryset()}
        return kwargs


class CapsuleContentSerializer(CapsuleRelatedSerializerMixin, serializers.HyperlinkedModelSerializer):
    metadata = BinaryField()

    class Meta:
        model = CapsuleContent
        fields = ["capsule", "data", "id", "metadata", "url"]


class CapsuleReceiverSerializer(CapsuleRelatedSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CapsuleReceiver
        fields = ["capsule", "email", "id", "url"]


class CapsuleReceiverConfirmationSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        if not self.instance.check_confirmation_token(value):
            raise ValidationError("Invalid token")
        return value
