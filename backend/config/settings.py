"""
Django settings for dachuang management system project.
"""

import os
from pathlib import Path
from datetime import timedelta
from django.core.management.utils import get_random_secret_key

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
LOCAL_DATA_DIR = PROJECT_ROOT / ".local" / "backend"


def _env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_list(name: str, default: list[str]) -> list[str]:
    value = os.environ.get(name)
    if value is None:
        return default
    parsed = [item.strip() for item in value.split(",") if item.strip()]
    return parsed or default


def _env_value(name: str) -> str | None:
    value = os.environ.get(name)
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _env_int(name: str, default: int) -> int:
    value = _env_value(name)
    if value is None:
        return default
    try:
        parsed = int(value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer.") from exc
    if parsed <= 0:
        raise RuntimeError(f"{name} must be greater than 0.")
    return parsed


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = _env_bool("DJANGO_DEBUG", True)

_secret_key = _env_value("DJANGO_SECRET_KEY")
if not DEBUG and (not _secret_key or _secret_key == "change-me-to-a-long-random-string"):
    raise RuntimeError("DJANGO_SECRET_KEY must be set to a strong value when DJANGO_DEBUG=false.")

# SECURITY WARNING: keep the secret key used in production secret.
SECRET_KEY = _secret_key or get_random_secret_key()

DEFAULT_USER_PASSWORD = _env_value("DEFAULT_USER_PASSWORD")
DEFAULT_RESET_PASSWORD = _env_value("DEFAULT_RESET_PASSWORD")

_WEAK_SHARED_PASSWORDS = {"123456", "admin123456", "password", "password123"}
if not DEBUG:
    for _password_name, _password_value in {
        "DEFAULT_USER_PASSWORD": DEFAULT_USER_PASSWORD,
        "DEFAULT_RESET_PASSWORD": DEFAULT_RESET_PASSWORD,
    }.items():
        if _password_value and (
            _password_value in _WEAK_SHARED_PASSWORDS or len(_password_value) < 12
        ):
            raise RuntimeError(
                f"{_password_name} must not use a weak shared value in production."
            )

ALLOWED_HOSTS = _env_list("DJANGO_ALLOWED_HOSTS", ["localhost", "127.0.0.1"] if DEBUG else [])
if not DEBUG and not ALLOWED_HOSTS:
    raise RuntimeError("DJANGO_ALLOWED_HOSTS must be configured when DJANGO_DEBUG=false.")

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party apps
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    # Local apps
    "apps.users",
    "apps.projects",
    "apps.reviews",
    "apps.notifications",
    "apps.dictionaries",
    "apps.system_settings",
    "apps.operations",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"

# Database
_db_name = os.environ.get("DB_NAME") or "dachuang_db"
_db_user = os.environ.get("DB_USER") or "postgres"
_db_password = os.environ.get("DB_PASSWORD") or ""
_db_host = os.environ.get("DB_HOST") or "localhost"
_db_port = os.environ.get("DB_PORT") or "5432"

if not DEBUG and (
    not _db_password
    or _db_password in _WEAK_SHARED_PASSWORDS
    or len(_db_password) < 12
):
    raise RuntimeError("DB_PASSWORD must be configured as a strong value in production.")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": _db_name,
        "USER": _db_user,
        "PASSWORD": _db_password,
        "HOST": _db_host,
        "PORT": _db_port,
    }
}

# Custom User Model
AUTH_USER_MODEL = "users.User"

# Password validation
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
LANGUAGE_CODE = "zh-hans"

TIME_ZONE = "Asia/Shanghai"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"
_media_root = os.environ.get("DJANGO_MEDIA_ROOT")
if not _media_root:
    _media_root = str(LOCAL_DATA_DIR / "media")
MEDIA_ROOT = str(Path(_media_root))
Path(MEDIA_ROOT).mkdir(parents=True, exist_ok=True)

# Upload resource limits. Per-field validators still enforce tighter business rules.
FILE_UPLOAD_MAX_MEMORY_SIZE = _env_int(
    "DJANGO_FILE_UPLOAD_MAX_MEMORY_SIZE",
    5 * 1024 * 1024,
)
DATA_UPLOAD_MAX_MEMORY_SIZE = _env_int(
    "DJANGO_DATA_UPLOAD_MAX_MEMORY_SIZE",
    25 * 1024 * 1024,
)
DATA_UPLOAD_MAX_NUMBER_FILES = _env_int("DJANGO_DATA_UPLOAD_MAX_NUMBER_FILES", 20)
DATA_UPLOAD_MAX_NUMBER_FIELDS = _env_int("DJANGO_DATA_UPLOAD_MAX_NUMBER_FIELDS", 2000)

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
}

# JWT Settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = _env_bool("DJANGO_CORS_ALLOW_ALL_ORIGINS", DEBUG)
CORS_ALLOWED_ORIGINS = _env_list("DJANGO_CORS_ALLOWED_ORIGINS", [])
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = _env_list("DJANGO_CSRF_TRUSTED_ORIGINS", [])

if not DEBUG and CORS_ALLOW_ALL_ORIGINS:
    raise RuntimeError("DJANGO_CORS_ALLOW_ALL_ORIGINS must be false in production.")

if not DEBUG and not CORS_ALLOWED_ORIGINS:
    raise RuntimeError("DJANGO_CORS_ALLOWED_ORIGINS must be configured in production.")

# Security headers and proxy-aware HTTPS settings
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = _env_bool("DJANGO_SECURE_SSL_REDIRECT", not DEBUG)
SESSION_COOKIE_SECURE = _env_bool("DJANGO_SESSION_COOKIE_SECURE", not DEBUG)
CSRF_COOKIE_SECURE = _env_bool("DJANGO_CSRF_COOKIE_SECURE", not DEBUG)
SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_SECURE_HSTS_SECONDS", "0" if DEBUG else "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = _env_bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", not DEBUG)
SECURE_HSTS_PRELOAD = _env_bool("DJANGO_SECURE_HSTS_PRELOAD", False)
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Logging
# Ensure log directory exists
_log_dir = os.environ.get("DJANGO_LOG_DIR")
if not _log_dir:
    _log_dir = str(LOCAL_DATA_DIR / "logs")
LOG_DIR = Path(_log_dir)
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_MAX_BYTES = _env_int("DJANGO_LOG_MAX_BYTES", 10 * 1024 * 1024)
LOG_BACKUP_COUNT = _env_int("DJANGO_LOG_BACKUP_COUNT", 5)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            # Use absolute path to avoid issues with working directory
            "filename": str(LOG_DIR / "debug.log"),
            "maxBytes": LOG_MAX_BYTES,
            "backupCount": LOG_BACKUP_COUNT,
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
}

# Celery / async task settings
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get(
    "CELERY_RESULT_BACKEND", CELERY_BROKER_URL
)
CELERY_TASK_ALWAYS_EAGER = _env_bool("CELERY_TASK_ALWAYS_EAGER", DEBUG)
CELERY_TASK_EAGER_PROPAGATES = False
