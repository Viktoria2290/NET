"""Конфигурация маршрутов URL для приложения Django.

Определяет соответствие URL-путей и view-функций, включая маршруты для admin-панели
и пользовательских views.
"""
from django.urls import path
from django.contrib import admin
from .views import index, login_view, register, upload_file, delete_doc, analyse_doc, get_text, cart, payment

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('login/', login_view, name='login'),
    path('register/', register, name='register'),
    path('upload_file/', upload_file, name='upload_file'),
    path('delete_doc/', delete_doc, name='delete_doc'),
    path('analyse_doc/', analyse_doc, name='analyse_doc'),
    path('get_text/', get_text, name='get_text'),
    path('cart/', cart, name='cart'),
    path('payment/', payment, name='payment'),
]
