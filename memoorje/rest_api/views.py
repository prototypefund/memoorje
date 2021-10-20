from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from memoorje import get_authenticated_user
from memoorje.models import Capsule, CapsuleContent, CapsuleReceiver
from memoorje.rest_api.serializers import (
    CapsuleContentSerializer,
    CapsuleReceiverConfirmationSerializer,
    CapsuleReceiverSerializer,
    CapsuleSerializer,
)


class CapsuleViewSet(viewsets.ModelViewSet):
    """
    Capsule access for authenticated users
    """

    serializer_class = CapsuleSerializer

    def get_queryset(self):
        return Capsule.objects.filter(owner=get_authenticated_user(self.request))


class CapsuleContentViewSet(viewsets.ModelViewSet):
    """
    Capsule content access for authenticated users
    """

    serializer_class = CapsuleContentSerializer
    filterset_fields = ["capsule"]

    def get_queryset(self):
        return CapsuleContent.objects.filter(capsule__owner=get_authenticated_user(self.request))


class CapsuleReceiverViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    Capsule content access for authenticated users
    """

    serializer_class = CapsuleReceiverSerializer
    filterset_fields = ["capsule"]

    def get_queryset(self):
        if self.action == "confirm":
            return CapsuleReceiver.objects
        return CapsuleReceiver.objects.filter(capsule__owner=get_authenticated_user(self.request))

    def get_permissions(self):
        if self.action == "confirm":
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "confirm":
            return CapsuleReceiverConfirmationSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_confirm(instance, serializer)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_confirm(self, instance, serializer):
        instance.confirm_email()
