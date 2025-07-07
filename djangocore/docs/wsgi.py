"""Конфигурация WSGI для запуска приложения Django.

Определяет точку входа для WSGI-совместимых серверов.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'docs.settings')
application = get_wsgi_application()
