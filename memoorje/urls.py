from django.contrib import admin
from django.urls import include, path

from memoorje.views import CapsuleContentDataDownloadView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("memoorje.rest_api.urls")),
    path("data/<int:pk>/", CapsuleContentDataDownloadView.as_view(), name="capsule-content-data"),
]
