from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from memoorje.models import Capsule, CapsuleContent
from memoorje.rest_api.permissions import IsCapsuleOwner
from memoorje.rest_api.serializers import CapsuleContentSerializer, CapsuleSerializer


class CapsuleViewSet(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    """
    Capsule access for authenticated users
    """

    queryset = Capsule.objects.all()
    serializer_class = CapsuleSerializer

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated & IsCapsuleOwner]
        return [permission() for permission in permission_classes]


class CapsuleContentViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = CapsuleContent.objects.all()
    serializer_class = CapsuleContentSerializer
    permission_classes = [IsAuthenticated & IsCapsuleOwner]

    def create(self, request, *args, **kwargs):
        """
        Create a content object for a given capsule.
        """
        return super().create(request, *args, **kwargs)

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
