from django.contrib import admin
from django.urls import include, path
from django_downloadview import ObjectDownloadView

from memoorje.models import CapsuleContent

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("memoorje.rest_api.urls")),
    path(
        "data/<int:pk>/",
        ObjectDownloadView.as_view(model=CapsuleContent, file_field="data"),
        name="capsule-content-data",
    ),
]
