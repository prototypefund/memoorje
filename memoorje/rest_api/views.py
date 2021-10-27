from djeveric.views import ConfirmModelMixin
from rest_framework import mixins, viewsets

from memoorje import get_authenticated_user
from memoorje.models import Capsule, CapsuleContent, CapsuleReceiver, Keyslot
from memoorje.rest_api.serializers import (
    CapsuleContentSerializer,
    CapsuleReceiverSerializer,
    CapsuleSerializer,
    KeyslotSerializer,
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
    """Capsule content access for authenticated users"""

    queryset = CapsuleReceiver.objects
    serializer_class = CapsuleReceiverSerializer
    filterset_fields = ["capsule"]

    def get_basic_queryset(self):
        return self.queryset.filter(capsule__owner=get_authenticated_user(self.request))


class KeyslotViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Keyslot access for authenticated users"""

    serializer_class = KeyslotSerializer
    filterset_fields = ["capsule"]

    def get_queryset(self):
        return Keyslot.objects.filter(capsule__owner=get_authenticated_user(self.request))
