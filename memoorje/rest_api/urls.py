from django.urls import include, path
from rest_framework import routers

from memoorje.rest_api.views import CapsuleContentViewSet, CapsuleViewSet, CreateCapsuleViewSet

router = routers.SimpleRouter()
router.register(r"capsules", CreateCapsuleViewSet)
router.register(r"capsules", CapsuleViewSet)
router.register(r"capsule-contents", CapsuleContentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("rest_registration.api.urls")),
]
