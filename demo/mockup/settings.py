"""Ustawienia makiety UI — bez bazy danych, tylko do podglądu wyglądu.

Lokalnie: domyślnie DEBUG=1. Publicznie (np. przez Cloudflare Tunnel):
    DEBUG=0 PUBLIC_HOST=hydro.wnikiel.pl SECRET_KEY=... ./serve.sh
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.environ.get("DEBUG", "1") == "1"
SECRET_KEY = os.environ.get("SECRET_KEY", "mockup-only-not-a-secret" if DEBUG else "")
if not SECRET_KEY:
    raise RuntimeError("Ustaw SECRET_KEY przy DEBUG=0")

PUBLIC_HOST = os.environ.get("PUBLIC_HOST", "")
ALLOWED_HOSTS = ["localhost", "127.0.0.1"] + ([PUBLIC_HOST] if PUBLIC_HOST else [])
CSRF_TRUSTED_ORIGINS = [f"https://{PUBLIC_HOST}"] if PUBLIC_HOST else []

# Za Cloudflare Tunnel: TLS kończy się na Cloudflare, cloudflared przekazuje X-Forwarded-Proto.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True

INSTALLED_APPS = [
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "ui",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "ui.middleware.MockRoleMiddleware",
]

ROOT_URLCONF = "mockup.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "ui.context.mock_context",
            ],
        },
    },
]

WSGI_APPLICATION = "mockup.wsgi.application"

# Brak bazy — sesja w podpisanym cookie, wiadomości w sesji.
DATABASES = {}
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

LANGUAGE_CODE = "pl"
TIME_ZONE = "Europe/Warsaw"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
