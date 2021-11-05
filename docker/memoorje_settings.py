import os

import dj_database_url

from memoorje.settings import *

ALLOWED_HOSTS = [os.environ.get("ALLOWED_HOSTS", "*")]
DATABASES["default"] = dj_database_url.config(conn_max_age=600)
STATIC_ROOT = "/app/static"
MEDIA_ROOT = "/var/lib/memoorje/media"
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
