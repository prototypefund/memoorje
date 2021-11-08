from rest_framework import serializers

from memoorje import get_authenticated_user
from memoorje.models import Capsule, CapsuleContent, CapsuleReceiver, Keyslot, PartialKey, Trustee
from memoorje.rest_api.fields import BinaryField


class RelatedCapsuleSerializerMixin:
    """Restricts the queryset for the `capsule` field of the serializer to capsules of the current user."""

    def get_capsule_queryset(self):
        return Capsule.objects.filter(owner=get_authenticated_user(self.context.get("request")))

    def get_extra_kwargs(self):
        kwargs = super().get_extra_kwargs()
        kwargs["capsule"] = {"queryset": self.get_capsule_queryset()}
        return kwargs


class CapsuleSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Capsule
        fields = ["created_on", "description", "id", "name", "owner", "updated_on", "url"]


class CapsuleContentSerializer(RelatedCapsuleSerializerMixin, serializers.HyperlinkedModelSerializer):
    metadata = BinaryField()

    class Meta:
        model = CapsuleContent
        fields = ["capsule", "data", "id", "metadata", "url"]


class CapsuleReceiverSerializer(RelatedCapsuleSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CapsuleReceiver
        fields = ["capsule", "email", "id", "url"]


class KeyslotSerializer(RelatedCapsuleSerializerMixin, serializers.HyperlinkedModelSerializer):
    data = BinaryField()

    class Meta:
        model = Keyslot
        fields = ["capsule", "data", "id", "purpose", "url"]


class PartialKeySerializer(serializers.HyperlinkedModelSerializer):
    data = BinaryField()

    class Meta:
        model = PartialKey
        fields = ["capsule", "data"]

    def validate(self, data):
        data_hash = PartialKey.hash_key_data(data["data"])
        try:
            Trustee.objects.get(capsule=data["capsule"], partial_key_hash=data_hash)
            return data
        except Trustee.DoesNotExist:
            raise serializers.ValidationError("Partial key data seems to be invalid for this capsule", "invalid_key")


class TrusteeSerializer(RelatedCapsuleSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Trustee
        fields = ["capsule", "email", "id", "url"]
