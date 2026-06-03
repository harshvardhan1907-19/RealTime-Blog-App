"""
Django settings for blogproject project.
"""

import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import dj_database_url

# Load environment variables
load_dotenv()

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-6&9^ku11bwu0bta*300if8igjgw+kc(z=x2o7zpx%r3=ft6-5r'

# SECURITY WARNING: don't run with debug turned on in production!

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    'https://realtime-blog-app.onrender.com',
    'http://realtime-blog-app.onrender.com',
]

ALLOWED_HOSTS = [
    'realtime-blog-app.onrender.com',
    'localhost',
    '127.0.0.1',
]

# Cookie security
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# Base apps that are always installed
BASE_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blogapp',
    'rest_framework',
    'channels',
]

# Cloudinary apps (only in production)
CLOUDINARY_APPS = [
    'cloudinary_storage',
    'cloudinary',
]

IS_PRODUCTION = os.environ.get('DATABASE_URL') is not None

if IS_PRODUCTION:
    INSTALLED_APPS = BASE_APPS + CLOUDINARY_APPS
else:
    INSTALLED_APPS = BASE_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'blogproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'blogapp' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'blogapp.context_processors.notification_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'blogproject.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication'
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 3
}

ASGI_APPLICATION = 'blogproject.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Database
DATABASES = {
    'default': dj_database_url.config(default='sqlite:///db.sqlite3')
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = [
    'blogapp.backends.EmailOrUsernameBackend',
    'django.contrib.auth.backends.ModelBackend'
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'blogapp' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Whitenoise configuration (for production)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# python manage.py collectstatic --noinput
# Why: When DEBUG=False, Django doesn't serve static files automatically. collectstatic gathers all static files into STATIC_ROOT (one folder), and Whitenoise serves them efficiently in production.

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_REDIRECT_URL = 'post_list'
LOGIN_URL = "login"
LOGOUT_REDIRECT_URL = "login"

# ========== STORAGE CONFIGURATION (ONLY ONCE) ==========
# Determine if we're running on Render (production) or locally
# Determine if running on Render (production)

if IS_PRODUCTION:
    # Production (Render) - Use Cloudinary
    DEBUG = False
    STORAGES = {
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
    CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')

    INSTALLED_APPS += ['anymail']
    EMAIL_BACKEND = 'anymail.backends.brevo.EmailBackend'
    ANYMAIL = {
        'BREVO_API_KEY': os.environ.get('BREVO_API_KEY'),
    }

else:
    # Local development - Use local file storage
    DEBUG = True
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'blogapp' /'media'

    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = os.environ.get('EMAIL_HOST_USER')

    # When you deploy to Render:

    # 1. Render clones your GitHub code
    # 2. Runs Build Command: pip install -r requirements.txt
    # 3. Runs: python manage.py collectstatic --noinput
    #             │
    #             ▼
    #  Django CREATES staticfiles/ folder
    #  (on Render's server, NOT on your PC)
    #             │
    #             ▼
    #  Copies: blogapp/static/images/avatar.png
    #  Into:    staticfiles/images/avatar.png
    #             │
    #             ▼
    #  Your site serves images from /static/ URL
    #  (but files are actually in staticfiles/ folder on server)
