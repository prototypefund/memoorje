from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from memoorje.models import Capsule
from memoorje.serializers import CapsuleSerializer


class CapsuleViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Create capsules for an authenticated user.
    """

    queryset = Capsule.objects.all()
    serializer_class = CapsuleSerializer
    permission_classes = [IsAuthenticated]
