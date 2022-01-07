from django.contrib.auth import authenticate
from rest_framework import serializers

from memoorje_2fa.utils import get_token_max_value, is_2fa_enabled_for_user


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
