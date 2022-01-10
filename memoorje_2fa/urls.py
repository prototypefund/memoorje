from django.urls import path

from memoorje_2fa.views import TwoFactorView

urlpatterns = [
    path("two-factor/", TwoFactorView.as_view(), name="two-factor"),
]
