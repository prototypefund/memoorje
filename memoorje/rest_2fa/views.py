from django.http import Http404
from rest_framework import generics, mixins

from memoorje.rest_2fa.serializers import (
    TwoFactorBackupSerializer,
    TwoFactorBackupStatusSerializer,
    TwoFactorDeleteSerializer,
    TwoFactorSerializer,
)
from memoorje.rest_2fa.users import get_default_device_for_user, get_named_device_for_user


class TwoFactorView(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin, generics.GenericAPIView
):
    """Configure two-factor authentication for the user."""

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return super().destroy(request, *args, **kwargs)

    def get_object(self):
        device = get_default_device_for_user(self.request.user)
        if device is None:
            raise Http404()
        return device

    def get_serializer_class(self):
        if self.request.method == "DELETE":
            return TwoFactorDeleteSerializer
        return TwoFactorSerializer


class TwoFactorBackupView(mixins.CreateModelMixin, mixins.RetrieveModelMixin, generics.GenericAPIView):
    """Create backup tokens."""

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_object(self):
        device = get_named_device_for_user(self.request.user, "backup")
        if device is None:
            raise Http404()
        return device

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TwoFactorBackupStatusSerializer
        return TwoFactorBackupSerializer
