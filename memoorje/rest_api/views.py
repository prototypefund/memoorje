from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from memoorje.models import Capsule, CapsuleContent
from memoorje.rest_api.permissions import IsCapsuleOwner
from memoorje.rest_api.serializers import CapsuleContentSerializer, CapsuleSerializer


class CreateCapsuleViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Create a capsule for the authenticated user
    """

    queryset = Capsule.objects.all()
    serializer_class = CapsuleSerializer
    permission_classes = [IsAuthenticated]


class CapsuleViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    Capsule access for authenticated users
    """

    queryset = Capsule.objects.all()
    serializer_class = CapsuleSerializer
    permission_classes = [IsAuthenticated & IsCapsuleOwner]


class CapsuleContentViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Capsule content access for a given capsule
    """

    queryset = CapsuleContent.objects.all()
    serializer_class = CapsuleContentSerializer
    permission_classes = [IsAuthenticated & IsCapsuleOwner]
