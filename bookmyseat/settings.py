"""
Django settings for bookmyseat project.
"""

from pathlib import Path
import os
import dj_database_url

# -------------------------------
# BASE DIRECTORY
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------
# SECURITY
# -------------------------------
SECRET_KEY = os.environ.get("SECRET_KEY", "unsafe-secret-key")
DEBUG = os.environ.get("DEBUG", "True").lower() in ("1", "true", "yes")

# -------------------------------
# ALLOWED HOSTS (Railway + Local)
# -------------------------------
ALLOWED_HOSTS = [
    "*",
    ".railway.app",
    ".vercel.app",
    "127.0.0.1",
    "localhost",
]

RAILWAY_URL = os.environ.get("RAILWAY_URL")
if RAILWAY_URL:
    ALLOWED_HOSTS.append(RAILWAY_URL)

VERCEL_URL = os.environ.get("VERCEL_URL")
if VERCEL_URL:
    ALLOWED_HOSTS.append(VERCEL_URL)

# -------------------------------
# INSTALLED APPS
# -------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "movies",
    "users",
]

# -------------------------------
# MIDDLEWARE
# -------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# -------------------------------
# ROOT URLS
# -------------------------------
ROOT_URLCONF = "bookmyseat.urls"

# -------------------------------
# TEMPLATES
# -------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

# -------------------------------
# WSGI
# -------------------------------
WSGI_APPLICATION = "bookmyseat.wsgi.application"

# -------------------------------
# DATABASE (Railway uses DATABASE_URL)
# -------------------------------



# -------------------------------
# DATABASE
# -------------------------------
# Use DATABASE_URL from environment for Postgres (Render/Railway),
# otherwise fallback to local SQLite.
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Enable SSL for PostgreSQL (Production)
if DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
    DATABASES['default']['OPTIONS'] = {'sslmode': 'require'}


# -------------------------------
# PASSWORD VALIDATION
# -------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -------------------------------
# INTERNATIONALIZATION
# -------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# -------------------------------
# STATIC FILES (Whitenoise Required)
# -------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# -------------------------------
# MEDIA FILES
# -------------------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# -------------------------------
# DEFAULT AUTO FIELD
# -------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------------------------
# STRIPE KEYS
# -------------------------------
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")

# -------------------------------
# EMAIL SETTINGS
# -------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = "Movie Booking <noreply@bookmyseat.com>"

# -------------------------------
# LOGIN REDIRECTS
# -------------------------------
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"













