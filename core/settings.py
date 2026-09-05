"""
Django settings for core project.

Production-ready: every secret and environment-specific value comes from
environment variables. Nothing sensitive is hardcoded in this file.
"""

import os
from datetime import timedelta
from pathlib import Path

import dj_database_url
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Core security
# ---------------------------------------------------------------------------

SECRET_KEY = config(
    "DJANGO_SECRET_KEY",
    default="django-insecure-local-dev-only-do-not-use-in-production",
)

DEBUG = config("DEBUG", default=False, cast=bool)

# Comma-separated bare hostnames, no scheme
ALLOWED_HOSTS = [
    h.strip()
    for h in config("ALLOWED_HOSTS", default="localhost,127.0.0.1").split(",")
    if h.strip()
]

SPECTACULAR_SETTINGS = {
    "TITLE": "E-Commerce REST API",
    "DESCRIPTION": "Django REST API with JWT auth, RBAC, cart/orders, "
                   "and Razorpay payments with HMAC webhook verification.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# Comma-separated, MUST include the https:// scheme
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in config("CSRF_TRUSTED_ORIGINS", default="").split(",")
    if o.strip()
]

# Railway terminates TLS at its proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True


# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "drf_spectacular",
    # Third party
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    # Our apps
    "users",
    "products",
    "orders",
]

# CORS first, then security, then WhiteNoise, then the rest.
# (The old file had SecurityMiddleware listed twice and WhiteNoise last,
# which meant static files were served after the response was finalised.)
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"


# ---------------------------------------------------------------------------
# Database — Neon Postgres in production, SQLite locally
# ---------------------------------------------------------------------------

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=not DEBUG,
    )
}

# Neon's pooled endpoint runs PgBouncer in transaction mode, which does not
# support server-side cursors.
DISABLE_SERVER_SIDE_CURSORS = True


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# Static and media files
# ---------------------------------------------------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------------------------------
# DRF / JWT / CORS
# ---------------------------------------------------------------------------

CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=24),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}


# ---------------------------------------------------------------------------
# Razorpay — test credentials, from environment only
# ---------------------------------------------------------------------------

RAZORPAY_KEY_ID = config("RAZORPAY_KEY_ID", default="")
RAZORPAY_KEY_SECRET = config("RAZORPAY_KEY_SECRET", default="")


# ---------------------------------------------------------------------------
# Celery
# ---------------------------------------------------------------------------
# CELERY_TASK_ALWAYS_EAGER runs tasks synchronously in the web process.
# Set it True in production for now: there is no worker service deployed,
# so queued tasks would otherwise sit in the broker and never execute.
# Set it False once a dedicated Celery worker service is running.

CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_TASK_ALWAYS_EAGER = config("CELERY_TASK_ALWAYS_EAGER", default=True, cast=bool)
CELERY_TASK_EAGER_PROPAGATES = False


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------
# Without EMAIL_HOST_USER set, falls back to console output so local
# development and the deployed demo never fail on a missing credential.

EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")

if EMAIL_HOST_USER:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
    EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
    EMAIL_USE_TLS = True
    EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
    DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER)
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    DEFAULT_FROM_EMAIL = "noreply@example.com"

