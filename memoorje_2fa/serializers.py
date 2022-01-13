from django.contrib.auth import authenticate
from django.db import transaction
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_framework import serializers
from rest_framework.exceptions import ErrorDetail

from memoorje.models import User
from memoorje_2fa.users import (
    create_backup_tokens_for_user,
    create_default_device_for_user,
    get_named_device_for_user,
    is_2fa_enabled_for_user,
)
from memoorje_2fa.utils import get_token_max_value


class TwoFactorLoginSerializer(serializers.Serializer):
    login = serializers.EmailField()
    password = serializers.CharField()
    token = serializers.IntegerField(required=False, min_value=0, max_value=get_token_max_value())
    backup_token = serializers.CharField(required=False)

    def get_device(self, user):
        return get_named_device_for_user(user, "default" if self._has_default_token() else "backup")

    def get_token(self):
        return self.validated_data.get("token" if self._has_default_token() else "backup_token")

    def validate(self, data):
        user = authenticate(username=data["login"], password=data["password"])
        if user and is_2fa_enabled_for_user(user) and data.get("token") is None and data.get("backup_token") is None:
            raise serializers.ValidationError(
                "For users with 2FA enabled a token must be provided", code="provide-token"
            )
        return data

    def _has_default_token(self):
        return "token" in self.validated_data


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


class StaticTokenField(serializers.RelatedField):
    def to_representation(self, value):
        return value.token


class TwoFactorBackupSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tokens = StaticTokenField(many=True, read_only=True, source="token_set")

    class Meta:
        model = StaticDevice
        fields = ["tokens", "user"]

    def create(self, validated_data):
        return create_backup_tokens_for_user(validated_data["user"])

    def validate_user(self, user: User):
        if not is_2fa_enabled_for_user(user):
            raise serializers.ValidationError(
                "Backup tokens can only be created if 2FA is enabled", code="two-factor-disabled"
            )
        return user
