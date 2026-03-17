"""
Django settings for SAV Pharmacie project.
"""
import os
from pathlib import Path
from datetime import timedelta
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    # Local apps
    'apps.accounts',
    'apps.pharmacies',
    'apps.tickets',
    'apps.zones',
    'apps.interventions',
    'apps.notifications',
    'apps.dashboard',
    'apps.windev_sync',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

# ──────────────────────────────────────────────────────────
# Databases
# Architecture : VPS Django  ──(réseau)──►  MySQL sur serveur WinDev
#   - 'default' : sav_pharmacie (Django, lecture/écriture)
#   - 'windev'  : FacturationClient (WinDev, sync bidirectionnelle)
# Les deux bases sont sur le même serveur MySQL (celui de WinDev).
# En local (dev) : utiliser DB_ENGINE=sqlite pour tester sans MySQL.
# ──────────────────────────────────────────────────────────
DB_ENGINE = config('DB_ENGINE', default='mysql')

if DB_ENGINE == 'sqlite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config('DB_NAME', default='sav_pharmacie'),
            'USER': config('DB_USER', default='root'),
            'PASSWORD': config('DB_PASSWORD', default='xamil@IFE2025'),
            'HOST': config('DB_HOST', default='127.0.0.1'),
            'PORT': config('DB_PORT', default='3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        },
    }
#
# WinDev legacy database (read-only, raw SQL only)
WINDEV_DB_NAME = config('WINDEV_DB_NAME', default='')
if WINDEV_DB_NAME:
    DATABASES['windev'] = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': WINDEV_DB_NAME,
        'USER': config('WINDEV_DB_USER', default='sav_readonly'),
        'PASSWORD': config('WINDEV_DB_PASSWORD', default=''),
        'HOST': config('WINDEV_DB_HOST', default='127.0.0.1'),
        'PORT': config('WINDEV_DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'read_default_group': 'read',
        },
    }

DATABASE_ROUTERS = ['config.db_router.WindevRouter']

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Abidjan'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%S%z',
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(
        minutes=config('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', default=60, cast=int)
    ),
    'REFRESH_TOKEN_LIFETIME': timedelta(
        days=config('JWT_REFRESH_TOKEN_LIFETIME_DAYS', default=7, cast=int)
    ),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=DEBUG, cast=bool)
if not CORS_ALLOW_ALL_ORIGINS:
    CORS_ALLOWED_ORIGINS = config(
        'CORS_ALLOWED_ORIGINS',
        default='http://localhost:5173,http://localhost:3000',
        cast=Csv()
    )
CORS_ALLOW_CREDENTIALS = True

# DRF Spectacular (Swagger)
SPECTACULAR_SETTINGS = {
    'TITLE': 'SAV Pharmacie API',
    'DESCRIPTION': 'API pour la gestion des SAV des pharmacies - Communication avec WinDev',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'TAGS': [
        {'name': 'Auth', 'description': 'Authentification et gestion des tokens'},
        {'name': 'Pharmacies', 'description': 'Gestion des pharmacies'},
        {'name': 'Tickets', 'description': 'Gestion des tickets SAV'},
        {'name': 'Interventions', 'description': 'Rapports d\'intervention'},
        {'name': 'Zones', 'description': 'Zones géographiques'},
        {'name': 'Techniciens', 'description': 'Gestion des techniciens'},
        {'name': 'Dashboard', 'description': 'Tableau de bord et statistiques'},
        {'name': 'WinDev Sync', 'description': 'Synchronisation avec l\'application WinDev'},
    ],
}

# Email
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Google Maps
GOOGLE_MAPS_API_KEY = config('GOOGLE_MAPS_API_KEY', default='')

# File upload limits
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# ──────────────────────────────────────────────────────────
# Celery (synchronisation périodique WinDev ↔ Django)
# ──────────────────────────────────────────────────────────
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://127.0.0.1:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 300  # 5 min max par tâche

# Synchronisation périodique toutes les 2 minutes
CELERY_BEAT_SCHEDULE = {
    # ── WinDev → Django (lecture de FacturationClient) ──
    'sync-windev-to-django-fast': {
        'task': 'apps.windev_sync.tasks.sync_windev_to_django_incremental',
        'schedule': 120.0,  # 2 minutes
        'options': {'expires': 110},
    },
    # ── Django → WinDev (écriture dans FacturationClient) ──
    'sync-django-to-windev-fast': {
        'task': 'apps.windev_sync.tasks.sync_django_to_windev_incremental',
        'schedule': 120.0,  # 2 minutes
        'options': {'expires': 110},
    },
    # ── Sync complète (référentiels, moins fréquent) ──
    'sync-windev-full-referentials': {
        'task': 'apps.windev_sync.tasks.sync_windev_referentials',
        'schedule': 900.0,  # 15 minutes
        'options': {'expires': 850},
    },
}

# Intervalle de sync configurable via .env
SYNC_INTERVAL_SECONDS = config('SYNC_INTERVAL_SECONDS', default=120, cast=int)
