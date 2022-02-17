from django.db.models import Q
from djeveric.views import ConfirmModelMixin
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import exception_handler

from memoorje.models import Capsule, CapsuleContent, CapsuleRecipient, Keyslot, Trustee
from memoorje.rest_api.permissions import IsCapsuleOwner, IsCapsuleOwnerOrReadOnly
from memoorje.rest_api.serializers import (
    AbortCapsuleReleaseSerializer,
    CapsuleContentSerializer,
    CapsuleRecipientSerializer,
    CapsuleSerializer,
    KeyslotSerializer,
    PartialKeySerializer,
    TrusteeSerializer,
)
from memoorje.utils import get_authenticated_user, get_recipient_by_token


def full_details_exception_handler(exc, context):
    if isinstance(exc, APIException):
        exc.detail = exc.get_full_details()
    return exception_handler(exc, context)


class OwnedCapsuleRelatedQueryMixin:
    def get_query(self):
        user = get_authenticated_user(self.request)
        query = Q(capsule__owner=user)
        return query


class OwnedCapsuleRelatedQuerySetMixin(OwnedCapsuleRelatedQueryMixin):
    def get_queryset(self):
        return self.queryset.filter(self.get_query())


class OwnedOrReceivedCapsuleRelatedQuerySetMixin(OwnedCapsuleRelatedQuerySetMixin):
    """
    Restricts the query set to objects for which the capsule is either owned by the current user or for which a
    recipient token exists.
    """

    def get_query(self):
        query = super().get_query()
        recipient = get_recipient_by_token(self.request)
        if recipient is not None:
            query |= Q(capsule__recipients=recipient)
        return query


class CapsuleViewSet(OwnedOrReceivedCapsuleRelatedQuerySetMixin, viewsets.ModelViewSet):
    """Capsule access for authenticated users"""

    permission_classes = [IsCapsuleOwnerOrReadOnly]
    serializer_class = CapsuleSerializer
    queryset = Capsule.objects

    @action(detail=True, methods=["post"], url_path="abort-release")
    def abort_release(self, request, **kwargs):
        instance = self.get_object()
        serializer = AbortCapsuleReleaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not instance.is_released:
            self.perform_abort_release(instance, **serializer.data)
        else:
            raise ValidationError("Cannot abort release of an already released capsule.", code="already_released")
        return Response(serializer.data)

    def perform_abort_release(self, capsule, is_accidental):
        if not is_accidental:
            capsule.keyslots.filter(purpose=Keyslot.Purpose.SSS).delete()
            capsule.trustees.all().delete()
        capsule.partial_keys.all().delete()
        Capsule.objects.update(id=capsule.id, are_partial_key_invitations_sent=False)


class CapsuleContentViewSet(OwnedOrReceivedCapsuleRelatedQuerySetMixin, viewsets.ModelViewSet):
    """Capsule content access for authenticated users"""

    permission_classes = [IsCapsuleOwnerOrReadOnly]
    serializer_class = CapsuleContentSerializer
    queryset = CapsuleContent.objects
    filterset_fields = ["capsule"]


class CapsuleRecipientViewSet(OwnedCapsuleRelatedQueryMixin, ConfirmModelMixin, viewsets.ModelViewSet):
    """Capsule recipient access for authenticated users"""

    permission_classes = [IsCapsuleOwner]
    queryset = CapsuleRecipient.objects
    serializer_class = CapsuleRecipientSerializer
    filterset_fields = ["capsule"]

    def get_basic_queryset(self):
        return self.queryset.filter(self.get_query())


class KeyslotViewSet(OwnedOrReceivedCapsuleRelatedQuerySetMixin, viewsets.ModelViewSet):
    """Keyslot access for authenticated users"""

    permission_classes = [IsCapsuleOwnerOrReadOnly]
    serializer_class = KeyslotSerializer
    queryset = Keyslot.objects
    filterset_fields = ["capsule"]


class PartialKeyViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Partial Key deposit for trustees"""

    permission_classes = [AllowAny]
    serializer_class = PartialKeySerializer


class TrusteeViewSet(
    OwnedCapsuleRelatedQuerySetMixin,
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
