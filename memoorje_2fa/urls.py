from django.urls import path

from memoorje_2fa.views import TwoFactorBackupView, TwoFactorView

urlpatterns = [
    path("two-factor/", TwoFactorView.as_view(), name="two-factor"),
    path("two-factor/backup-tokens/", TwoFactorBackupView.as_view(), name="two-factor-backup"),
]
