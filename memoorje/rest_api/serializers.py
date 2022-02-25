from rest_framework import serializers

from memoorje.models import Capsule, CapsuleContent, CapsuleRecipient, Keyslot, PartialKey, Trustee, User
from memoorje.rest_api.fields import BinaryField, HexDigestField
from memoorje.utils import get_authenticated_user


class CapsuleRelatedSerializerMixin:
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


class CapsuleContentSerializer(CapsuleRelatedSerializerMixin, serializers.HyperlinkedModelSerializer):
    data_size_bytes = serializers.IntegerField(source="data.size", read_only=True)
    metadata = BinaryField()

    class Meta:
        model = CapsuleContent
        fields = ["capsule", "data", "data_size_bytes", "id", "metadata", "url"]


class CapsuleRecipientSerializer(CapsuleRelatedSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CapsuleRecipient
        fields = ["capsule", "email", "id", "is_active", "name", "url"]


class KeyslotSerializer(CapsuleRelatedSerializerMixin, serializers.HyperlinkedModelSerializer):
    data = BinaryField()

    class Meta:
        model = Keyslot
        fields = ["capsule", "data", "id", "purpose", "url"]


class PartialKeySerializer(serializers.HyperlinkedModelSerializer):
    data = BinaryField()

    class Meta:
        model = PartialKey
        fields = ["capsule", "data"]

    def validate_capsule(self, value):
        if value.is_released:
            raise serializers.ValidationError(
                "Capsule was already released, not accepting further keys", "already_released"
            )
        return value

    def validate(self, data):
        data_hash = PartialKey.hash_key_data(data["data"])
        try:
            Trustee.objects.get(capsule=data["capsule"], partial_key_hash=data_hash)
            return data
        except Trustee.DoesNotExist:
            raise serializers.ValidationError("Partial key data seems to be invalid for this capsule", "invalid_key")


class TrusteeSerializer(CapsuleRelatedSerializerMixin, serializers.HyperlinkedModelSerializer):
    partial_key_sha256 = HexDigestField(source="partial_key_hash", write_only=True)

    class Meta:
        model = Trustee
        fields = ["capsule", "email", "id", "name", "partial_key_sha256", "url"]


class UserSerializer(serializers.HyperlinkedModelSerializer):
    account_balance = serializers.DecimalField(max_digits=8, decimal_places=2, source="transactions.get_balance")

    class Meta:
        model = User
        fields = ["account_balance", "email", "id", "language", "name", "remind_interval"]


class AbortCapsuleReleaseSerializer(serializers.Serializer):
    is_accidental = serializers.BooleanField(default=True)
