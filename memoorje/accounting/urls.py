from django.urls import include, path
from rest_framework.routers import SimpleRouter

from memoorje.accounting.views import TransactionViewSet

router = SimpleRouter()
router.register(r"transactions", TransactionViewSet, basename="transaction")

urlpatterns = [
    path("", include(router.urls)),
]
