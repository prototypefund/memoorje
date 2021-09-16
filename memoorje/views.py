from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from memoorje.models import Capsule
from memoorje.serializers import CapsuleSerializer


class CapsuleViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Capsule access for authenticated users.
    """

    queryset = Capsule.objects.all()
    serializer_class = CapsuleSerializer
    permission_classes = [IsAuthenticated]
