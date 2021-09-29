from django.contrib import admin
from django.urls import include, path

from memoorje.views import CapsuleDataDownloadView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("memoorje.rest_api.urls")),
    path("data/<int:pk>/", CapsuleDataDownloadView.as_view(), name="capsule-data"),
]
