from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from memoorje.models import Capsule
from memoorje.serializers import CapsuleSerializer


class CapsuleViewSet(viewsets.ModelViewSet):
    """
    Create, list, show, update and delete the capsules for an authenticated user.
    """

    queryset = Capsule.objects.all()
    serializer_class = CapsuleSerializer
    permission_classes = [IsAuthenticated]
