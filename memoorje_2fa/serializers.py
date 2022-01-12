from django.contrib.auth import authenticate
from django.db import transaction
from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_framework import serializers
from rest_framework.exceptions import ErrorDetail

from memoorje.models import User
from memoorje_2fa.utils import get_token_max_value, get_totp_for_device
from memoorje_2fa.users import create_default_device_for_user, is_2fa_enabled_for_user


class TwoFactorLoginSerializer(serializers.Serializer):
    login = serializers.EmailField()
    password = serializers.CharField()
    token = serializers.IntegerField(required=False, min_value=0, max_value=get_token_max_value())

    def validate(self, data):
        user = authenticate(username=data["login"], password=data["password"])
        if user and is_2fa_enabled_for_user(user) and data.get("token") is None:
            raise serializers.ValidationError(
                "For users with 2FA enabled a token must be provided", code="provide-token"
            )
        return data


class TwoFactorSerializer(serializers.HyperlinkedModelSerializer):
    token = serializers.IntegerField(write_only=True, min_value=0, max_value=get_token_max_value())
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = TOTPDevice
        fields = ["key", "token", "user"]

    def create(self, validated_data):
        with transaction.atomic():
            device = create_default_device_for_user(validated_data["user"], key=validated_data["key"])
            if not device.verify_token(validated_data["token"]):
                # We raise a late ValidationError (after actual validation is already done). This is, as we cannot
                # verify the token without creating the device (the device updates the drift upon verification).
                raise serializers.ValidationError(
                    {"non_field_errors": [ErrorDetail("Token is not valid for the given key", code="invalid-token")]}
                )
            return device

    def validate_user(self, user: User):
        if is_2fa_enabled_for_user(user):
            raise serializers.ValidationError("2FA is already enabled for this user", code="already-enabled")
        return user
