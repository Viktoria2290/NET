"""Конфигурация маршрутов URL для приложения Django REST Framework.

Определяет маршруты для аутентификации через JWT, проксирования запросов к FastAPI
и получения файлов из S3.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import proxy_view, s3_get_view

urlpatterns = [
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('proxy/<path:path>', proxy_view, name='proxy'),
    path('s3/get/', s3_get_view, name='s3_get'),
]
