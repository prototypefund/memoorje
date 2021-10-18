from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from memoorje import get_authenticated_user
from memoorje.confirmations import CapsuleReceiverConfirmation
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
        return CapsuleReceiver.objects.filter(capsule__owner=get_authenticated_user(self.request))

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        serializer = CapsuleReceiverConfirmationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            CapsuleReceiverConfirmation(serializer.instance).check()
            return Response()
