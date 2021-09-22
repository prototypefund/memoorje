from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework import routers
from rest_registration.api.views import login, profile, register

from memoorje.rest_api.views import CapsuleContentViewSet, CapsuleViewSet, CreateCapsuleViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r"capsules", CreateCapsuleViewSet)
router.register(r"capsules", CapsuleViewSet)
router.register(r"capsule-contents", CapsuleContentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("auth/login", login, name="login"),
    path("auth/profile", profile, name="profile"),
    path("auth/register", register, name="register"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
