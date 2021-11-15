from django.db.models import Q
from djeveric.views import ConfirmModelMixin
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny

from memoorje.models import Capsule, CapsuleContent, CapsuleReceiver, Keyslot, Trustee
from memoorje.rest_api.permissions import IsCapsuleOwner, IsCapsuleOwnerOrReadOnly
from memoorje.rest_api.serializers import (
    CapsuleContentSerializer,
    CapsuleReceiverSerializer,
    CapsuleSerializer,
    KeyslotSerializer,
    PartialKeySerializer,
    TrusteeSerializer,
)
from memoorje.utils import get_authenticated_user, get_receiver_by_token


class CapsuleRelatedQuerySetMixin:
    """
    Restricts the query set to objects for which the capsule is either owned by the current user or for which a receiver
    token exists.
    """

    def get_queryset(self):
        user = get_authenticated_user(self.request)
        receiver = get_receiver_by_token(self.request)
        query = Q(capsule__owner=user)
        if receiver is not None:
            query |= Q(capsule__receivers=receiver)
        return self.queryset.filter(query)


class CapsuleViewSet(CapsuleRelatedQuerySetMixin, viewsets.ModelViewSet):
    """Capsule access for authenticated users"""

    permission_classes = [IsCapsuleOwnerOrReadOnly]
    serializer_class = CapsuleSerializer
    queryset = Capsule.objects


class CapsuleContentViewSet(CapsuleRelatedQuerySetMixin, viewsets.ModelViewSet):
    """Capsule content access for authenticated users"""

    permission_classes = [IsCapsuleOwnerOrReadOnly]
    serializer_class = CapsuleContentSerializer
    queryset = CapsuleContent.objects
    filterset_fields = ["capsule"]


class CapsuleReceiverViewSet(
    ConfirmModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Capsule receiver access for authenticated users"""

    permission_classes = [IsCapsuleOwner]
    queryset = CapsuleReceiver.objects
    serializer_class = CapsuleReceiverSerializer
    filterset_fields = ["capsule"]

    def get_basic_queryset(self):
        return self.queryset.filter(capsule__owner=get_authenticated_user(self.request))


class KeyslotViewSet(viewsets.ModelViewSet):
    """Keyslot access for authenticated users"""

    permission_classes = [IsCapsuleOwner]
    serializer_class = KeyslotSerializer
    queryset = Keyslot.objects
    filterset_fields = ["capsule"]


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

    permission_classes = [IsCapsuleOwner]
    serializer_class = TrusteeSerializer
    queryset = Trustee.objects
    filterset_fields = ["capsule"]
