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
from memoorje.rest_api.view_mixins import (
    OwnedCapsuleRelatedFilterMixin,
    OwnedCapsuleRelatedQuerySetMixin,
    OwnedOrReceivedCapsuleRelatedQuerySetMixin,
)


def full_details_exception_handler(exc, context):
    if isinstance(exc, APIException):
        exc.detail = exc.get_full_details()
    return exception_handler(exc, context)


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


class CapsuleRecipientViewSet(OwnedCapsuleRelatedFilterMixin, ConfirmModelMixin, viewsets.ModelViewSet):
    """Capsule recipient access for authenticated users"""

    permission_classes = [IsCapsuleOwner]
    queryset = CapsuleRecipient.objects
    serializer_class = CapsuleRecipientSerializer
    filterset_fields = ["capsule"]

    def get_basic_queryset(self):
        return self.queryset.filter(self.get_filter())

    @action(methods=["post"], detail=True, url_path="send-confirmation-email")
    def resend(self, request, pk=None):
        recipient: CapsuleRecipient = self.get_object()
        if recipient.is_active():
            raise ValidationError("Recipient is already confirmed", code="already-confirmed")
        recipient.send_confirmation_email()
        return Response()


class KeyslotViewSet(OwnedOrReceivedCapsuleRelatedQuerySetMixin, viewsets.ModelViewSet):
    """Keyslot access for authenticated users"""

    permission_classes = [IsCapsuleOwnerOrReadOnly]
    serializer_class = KeyslotSerializer
    queryset = Keyslot.objects
    filterset_fields = ["capsule"]

    def get_recipient_filter(self, recipient: CapsuleRecipient) -> Q:
        return Q(recipient=recipient)


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
