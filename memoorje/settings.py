"""
Django settings for memoorje project.

Generated by 'django-admin startproject' using Django 3.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import collections
import os
from pathlib import Path

from memoorje.emails import convert_html_to_text

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
    "memoorje.accounting",
    "memoorje.data_storage",
    "memoorje.rest_api",
    "memoorje.rest_2fa",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
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
LANGUAGES = [
    ("de", "Deutsch"),
    ("en", "English"),
]
DEFAULT_USER_LANGUAGE = "de"

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
    "EXCEPTION_HANDLER": "memoorje.rest_api.views.full_details_exception_handler",
    "JSON_UNDERSCOREIZE": {
        "no_underscore_before_number": True,
    },
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

REST_REGISTRATION = {
    "REGISTER_VERIFICATION_ENABLED": True,
    "REGISTER_VERIFICATION_EMAIL_SENDER": "memoorje.models.send_registration_confirmation",
    "REGISTER_EMAIL_VERIFICATION_ENABLED": False,
    "RESET_PASSWORD_VERIFICATION_ENABLED": True,
    "RESET_PASSWORD_VERIFICATION_EMAIL_SENDER": "memoorje.models.send_reset_password_email",
    "LOGIN_AUTHENTICATOR": "memoorje.rest_2fa.users.authenticate",
    "LOGIN_SERIALIZER_CLASS": "memoorje.rest_2fa.serializers.TwoFactorLoginSerializer",
    "PROFILE_SERIALIZER_CLASS": "memoorje.rest_api.serializers.UserSerializer",
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

CAPSULE_RELEASE_GRACE_PERIOD_DAYS = 3

TWO_FACTOR_BACKUP_TOKEN_COUNT = 10

TEMPLATED_EMAIL_PLAIN_FUNCTION = convert_html_to_text

TEMPLATED_EMAIL_TEMPLATE_DIR = "emails/"


class _OriginPrefixedURLs(collections.UserDict):
    def __getitem__(self, item):
        from django.conf import settings

        return settings.ORIGIN + self.data[item]

    def __repr__(self):
        return repr({key: self[key] for key in self.keys()})


ORIGIN = "http://localhost:8000"

FRONTEND_LINKS = _OriginPrefixedURLs(
    {
        "capsule_hints_justify": "#",
        "capsule_release_abort": "/my/capsules/{pk}/abort-release",
        "capsule_release_abort_justify": "#",
        "capsule_token_access": "/-/capsules/{pk}?token={token}",
        "capsule_token_access_justify": "#",
        "capsule_recipient_confirm": "/-/capsule-recipients/{pk}/confirm?token={token}",
        "capsule_recipient_confirm_justify": "#",
        "partial_key_create": "/-/capsules/{capsule_pk}/release",
        "partial_key_create_justify": "#",
        "user_journal_justify": "#",
        "user_password_reset": "/auth/reset-password?userId={user_id}&timestamp={timestamp}&signature={signature}",
        "user_password_reset_justify": "#",
        "user_registration_confirm": "/auth/confirm-user?userId={user_id}&timestamp={timestamp}&signature={signature}",
        "user_registration_confirm_justify": "#",
        "user_reminder_check": "/my/capsules",
        "user_reminder_check_justify": "#",
    }
)

MONTHLY_DUE_PER_CAPSULE = 1

CURRENCY_REPRESENTATION = {
    "max_digits": 8,
    "decimal_places": 2,
}

EXPENSE_TYPE_AMOUNT_SUM_REFERENCE_PERIOD_MONTHS = 6

JOURNAL_NOTIFICATION_GRACE_PERIOD_MINUTES = 5

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
