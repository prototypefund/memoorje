from djeveric.views import ConfirmModelMixin
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny

from memoorje import get_authenticated_user
from memoorje.models import Capsule, CapsuleContent, CapsuleReceiver, Keyslot, Trustee
from memoorje.rest_api.serializers import (
    CapsuleContentSerializer,
    CapsuleReceiverSerializer,
    CapsuleSerializer,
    KeyslotSerializer,
    PartialKeySerializer,
    TrusteeSerializer,
)


class CapsuleViewSet(viewsets.ModelViewSet):
    """Capsule access for authenticated users"""

    serializer_class = CapsuleSerializer

    def get_queryset(self):
        return Capsule.objects.filter(owner=get_authenticated_user(self.request))


class CapsuleContentViewSet(viewsets.ModelViewSet):
    """Capsule content access for authenticated users"""

    serializer_class = CapsuleContentSerializer
    filterset_fields = ["capsule"]

    def get_queryset(self):
        return CapsuleContent.objects.filter(capsule__owner=get_authenticated_user(self.request))


class CapsuleReceiverViewSet(
    ConfirmModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Capsule receiver access for authenticated users"""

    queryset = CapsuleReceiver.objects
    serializer_class = CapsuleReceiverSerializer
    filterset_fields = ["capsule"]

    def get_basic_queryset(self):
        return self.queryset.filter(capsule__owner=get_authenticated_user(self.request))


class KeyslotViewSet(viewsets.ModelViewSet):
    """Keyslot access for authenticated users"""

    serializer_class = KeyslotSerializer
    filterset_fields = ["capsule"]

    def get_queryset(self):
        return Keyslot.objects.filter(capsule__owner=get_authenticated_user(self.request))


class PartialKeyViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Partial Key deposit for trustees"""

    permission_classes = [AllowAny]
    serializer_class = PartialKeySerializer


class TrusteeViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Trustee access for authenticated users"""

    serializer_class = TrusteeSerializer
    filterset_fields = ["capsule"]

    def get_queryset(self):
        return Trustee.objects.filter(capsule__owner=get_authenticated_user(self.request))
