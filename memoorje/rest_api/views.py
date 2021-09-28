from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from memoorje.models import Capsule, CapsuleContent
from memoorje.rest_api.permissions import IsCapsuleOwner
from memoorje.rest_api.serializers import CapsuleContentSerializer, CapsuleSerializer


class CapsuleViewSet(viewsets.ModelViewSet):
    """
    Capsule access for authenticated users
    """

    serializer_class = CapsuleSerializer

    def get_permissions(self):
        if self.action in ["create", "list"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated & IsCapsuleOwner]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return Capsule.objects.filter(owner=self.request.user)


class CapsuleContentViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    """
    Capsule content access for authenticated users
    """

    serializer_class = CapsuleContentSerializer
    permission_classes = [IsAuthenticated & IsCapsuleOwner]

    def get_queryset(self):
        return CapsuleContent.objects.filter(capsule__owner=self.request.user)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="capsule", description="`id` of the capsule to which the content belongs", required=True, type=str
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        List the content objects for a given capsule.
        """
        return super().list(request, *args, **kwargs)
