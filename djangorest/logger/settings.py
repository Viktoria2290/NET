"""Настройки проекта Django для управления конфигурацией REST API приложения.

Модуль определяет параметры для подключения к базе данных, кэширования,
логирования через Loki, работы с S3, Celery и Channels.
"""
import os
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_REST_SECRET_KEY', 'django-insecure-!@#$%^&*()')
DEBUG = os.getenv('DJANGO_REST_DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'rest_framework',
    'rest_framework_simplejwt',
    'logger',
    'channels',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'logger.middleware.LoggingMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

ROOT_URLCONF = 'logger.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'logger.wsgi'
ASGI_APPLICATION = 'logger.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('redis', 6379)],
        },
    },
}

def configure_database():
    """Настраивает подключение к базе данных на основе переменной окружения DATABASE_URL.

    Returns:
        dict: Конфигурация базы данных для Django.
    """
    DATABASE_URL = os.getenv('DJANGO_REST_DATABASE_URL')
    if DATABASE_URL.startswith('sqlite'):
        parsed_url = urlparse(DATABASE_URL)
        db_path = parsed_url.path[1:]  # Удаляет начальный символ '/'
        return {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': db_path,
            }
        }
    else:
        raise ValueError("Поддерживается только SQLite в данной конфигурации")

DATABASES = configure_database()

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')

AWS_S3_ENDPOINT_URL = os.getenv('S3_URL')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('BUCKET_NAME')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'loki': {
            'class': 'logging.handlers.HTTPHandler',
            'host': 'loki:3100',
            'url': '/loki/api/v1/push',
            'method': 'POST',
            'formatter': 'json',
        },
    },
    'formatters': {
        'json': {
            'format': '{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "user": "%(user)s", "ip": "%(ip)s", "service": "djangorest", "endpoint": "%(endpoint)s", "method": "%(method)s", "status": "%(status)s", "location": "%(location)s"}',
        },
    },
    'loggers': {
        'djangorest': {
            'handlers': ['loki'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
