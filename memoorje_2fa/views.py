from rest_framework import generics, mixins

from memoorje_2fa.serializers import TwoFactorSerializer


class TwoFactorView(mixins.CreateModelMixin, generics.GenericAPIView):
    """Configure two-factor authentication for the user."""

    serializer_class = TwoFactorSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
