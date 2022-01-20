from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("memoorje.rest_api.urls")),
    path("api/data/", include("memoorje.data_storage.urls")),
]
