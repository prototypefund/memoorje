from django.urls import include, path
from rest_framework.routers import SimpleRouter

from memoorje.accounting.views import ExpenseTypeViewSet, TransactionViewSet

router = SimpleRouter()
router.register(r"expense-types", ExpenseTypeViewSet, basename="expensetype")
router.register(r"transactions", TransactionViewSet, basename="transaction")

urlpatterns = [
    path("", include(router.urls)),
]
