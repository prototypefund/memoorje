from django.urls import path

from memoorje.data_storage.views import CapsuleDataDownloadView

urlpatterns = [
    path("<int:pk>/", CapsuleDataDownloadView.as_view(), name="capsule-data"),
]
