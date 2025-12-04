"""
Django settings for bookmyseat project.
"""

from pathlib import Path
import os
import dj_database_url

# -------------------------------
# BASE DIR
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------
# SECURITY
# -------------------------------
SECRET_KEY = os.environ.get('SECRET_KEY', 'unsafe-dev-key')
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('1', 'true', 'yes')

# -------------------------------
# ALLOWED HOSTS
# -------------------------------
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '.vercel.app').split(',')

# -------------------------------
# INSTALLED APPS
# -------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Your apps
    'movies',
]

# -------------------------------
# MIDDLEWARE
# -------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# -------------------------------
# ROOT URLS
# -------------------------------
ROOT_URLCONF = 'bookmyseat.urls'

# -------------------------------
# TEMPLATES
# -------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# -------------------------------
# WSGI
# -------------------------------
WSGI_APPLICATION = 'bookmyseat.wsgi.application'

# -------------------------------
# DATABASE
# Use DATABASE_URL from environment (PostgreSQL)
# -------------------------------
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True  # Required for Neon/PostgreSQL on Vercel
    )
}

# -------------------------------
# PASSWORD VALIDATORS
# -------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------------------
# INTERNATIONALIZATION
# -------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -------------------------------
# STATIC FILES (CSS, JS, Images)
# -------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Where collectstatic will place files
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # Your local static files
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# -------------------------------
# DEFAULT AUTO FIELD
# -------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'











