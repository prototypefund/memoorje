"""
Django settings for memoorje project.

Generated by 'django-admin startproject' using Django 3.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("MEMOORJE_DATA_DIR", BASE_DIR))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-ngy2599=i5c*5(*bw%gbs&jzb(^p-4zk&6!a8a76tevv$tb9xq"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_filters",
    "django_otp",
    "django_otp.plugins.otp_static",
    "django_otp.plugins.otp_totp",
    "drf_spectacular",
    "rest_framework",
    "rest_registration",
    "memoorje",
    "memoorje.data_storage",
    "memoorje.rest_api",
    "memoorje.rest_2fa",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "memoorje.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "memoorje.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DATA_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "de-de"

TIME_ZONE = "Europe/Berlin"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# media
MEDIA_ROOT = DATA_DIR / "media"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = DATA_DIR / "static"


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "memoorje.User"

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "djangorestframework_camel_case.parser.CamelCaseFormParser",
        "djangorestframework_camel_case.parser.CamelCaseMultiPartParser",
        "djangorestframework_camel_case.parser.CamelCaseJSONParser",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
        "djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

REST_REGISTRATION = {
    "LOGIN_AUTHENTICATOR": "memoorje.rest_2fa.users.authenticate",
    "LOGIN_SERIALIZER_CLASS": "memoorje.rest_2fa.serializers.TwoFactorLoginSerializer",
    "REGISTER_VERIFICATION_ENABLED": False,
    "REGISTER_EMAIL_VERIFICATION_ENABLED": False,
    "RESET_PASSWORD_VERIFICATION_ENABLED": False,
    "USER_HIDDEN_FIELDS": [
        "date_joined",
        "groups",
        "is_active",
        "is_staff",
        "is_superuser",
        "last_login",
        "last_reminder_sent_on",
        "user_permissions",
    ],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Memoorje API",
    "DESCRIPTION": "Sicherer, selbstverwalteter digitaler Nachlass für alle",
    "VERSION": "0.0.1",
    "POSTPROCESSING_HOOKS": ["drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields"],
}

CAPSULE_DATA_DIR = MEDIA_ROOT / "data"

DEFAULT_REMIND_INTERVAL_MONTHS = 6

RECIPIENT_PASSWORD_LENGTH = 32

SECRET_SHARE_COMBINE_PATH = Path("~/.cargo/bin/secret-share-combine").expanduser()

INACTIVE_RECIPIENT_HINT_DAYS = 7

TRUSTEE_PARTIAL_KEY_INVITATION_GRACE_PERIOD_DAYS = 3

TWO_FACTOR_BACKUP_TOKEN_COUNT = 10

TEMPLATED_EMAIL_TEMPLATE_DIR = "emails/"

FRONTEND_LINKS = {
    "capsule_release_abort": "http://localhost:8080/capsules/{pk}/release/abort",
    "capsule_release_abort_justify": "#",
    "capsule_token_access": "http://localhost:8080/capsules/{pk}/recipient_access/{token}",
    "capsule_token_access_justify": "#",
    "capsule_recipient_change_justify": "#",
    "capsule_recipient_confirm": "http://localhost:8080/capsule-recipients/{pk}/confirm/{token}",
    "capsule_recipient_confirm_justify": "#",
    "partial_key_create": "http://localhost:8080/capsules/{capsule_pk}/partial-keys/add",
    "partial_key_create_justify": "#",
    "user_reminder_check": "http://localhost:8080/capsules/check",
    "user_reminder_check_justify": "#",
}
