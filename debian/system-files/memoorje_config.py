# Copy this file to /etc/memoorje and adapt it to your needs

import logging

from memoorje.settings import *

# Configure logging for your needs.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": logging.getLevelName(logging.INFO),
    },
}

# mail settings
EMAIL_HOST = "my-mail-host"
EMAIL_PORT = 587
EMAIL_HOST_USER = "user"
EMAIL_HOST_PASSWORD = "password"
EMAIL_USE_TLS = True

# database settings
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": "localhost",
        "NAME": "name",
        "USER": "user",
        "PASSWORD": "password",
    }
}

# django file handling
MEDIA_ROOT = "/var/lib/memoorje/media"
STATIC_ROOT = "/var/lib/memoorje/static"

# security
SECRET_KEY = None
ALLOWED_HOSTS.append("memoorje.org")
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False
