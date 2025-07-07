"""Конфигурация WSGI для запуска приложения Django.

Определяет точку входа для WSGI-совместимых серверов, таких как Gunicorn или uWSGI.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logger.settings')
application = get_wsgi_application()
