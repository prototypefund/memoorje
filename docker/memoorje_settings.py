import os

import dj_database_url

from memoorje.settings import *

ALLOWED_HOSTS = [os.environ.get("ALLOWED_HOSTS", "*")]
DATABASES["default"] = dj_database_url.config(conn_max_age=600)
STATIC_ROOT = "/app/static"
MEDIA_ROOT = "/var/lib/memoorje/media"
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

ORIGIN = os.environ.get("MEMOORJE_ORIGIN", ORIGIN)
USE_X_FORWARDED_HOST = True

EMAIL_HOST = os.environ.get("MEMOORJE_EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.environ.get("MEMOORJE_EMAIL_PORT", 25))
EMAIL_USE_TLS = os.environ.get("MEMOORJE_EMAIL_USE_TLS", "False") == "True"
DEFAULT_FROM_EMAIL = os.environ.get("MEMOORJE_DEFAULT_FROM_EMAIL", "noreply@example.com")
