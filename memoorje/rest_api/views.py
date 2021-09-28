from rest_framework import mixins, viewsets

from memoorje.models import Capsule, CapsuleContent
from memoorje.rest_api.serializers import CapsuleContentSerializer, CapsuleSerializer


class CapsuleViewSet(viewsets.ModelViewSet):
    """
    Capsule access for authenticated users
    """

    serializer_class = CapsuleSerializer

    def get_queryset(self):
        return Capsule.objects.filter(owner=self.request.user)


class CapsuleContentViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    """
    Capsule content access for authenticated users
    """

    serializer_class = CapsuleContentSerializer
    filterset_fields = ["capsule"]

    def get_queryset(self):
        return CapsuleContent.objects.filter(capsule__owner=self.request.user)
