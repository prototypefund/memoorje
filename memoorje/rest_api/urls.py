from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework import routers

from memoorje.rest_api.views import (
    CapsuleContentViewSet,
    CapsuleReceiverViewSet,
    CapsuleViewSet,
    KeyslotViewSet,
    TrusteeViewSet,
)

router = routers.SimpleRouter()
router.register(r"capsules", CapsuleViewSet, basename="capsule")
router.register(r"capsule-contents", CapsuleContentViewSet, basename="capsulecontent")
router.register(r"capsule-receivers", CapsuleReceiverViewSet, basename="capsulereceiver")
router.register(r"keyslots", KeyslotViewSet, basename="keyslot")
router.register(r"trustees", TrusteeViewSet, basename="trustee")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("rest_registration.api.urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
