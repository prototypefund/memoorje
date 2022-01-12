from django.http import Http404
from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_framework import generics, mixins
from rest_framework.generics import get_object_or_404

from memoorje_2fa.serializers import TwoFactorSerializer
from memoorje_2fa.users import get_default_device_for_user


class TwoFactorView(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin, generics.GenericAPIView
):
    """Configure two-factor authentication for the user."""

    serializer_class = TwoFactorSerializer

    def delete(self, *args, **kwargs):
        return self.destroy(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.retrieve(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self.create(*args, **kwargs)

    def get_object(self):
        device = get_default_device_for_user(self.request.user)
        if device is None:
            raise Http404
        return device
