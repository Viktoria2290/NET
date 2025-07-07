"""Модуль views для обработки HTTP-запросов и рендеринга templates.

Содержит view-функции для аутентификации, загрузки файлов, управления документами,
анализа документов, работы с корзиной и оплаты.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from .models import Docs, UsersToDocs, Price, Cart
from .forms import UploadFileForm, DeleteDocForm, AnalyseDocForm, GetTextForm
import requests
import os
import boto3
import json
import base64


def get_api_headers():
    """Формирует заголовки для API-запросов с использованием JWT-токена.

    Returns:
        dict: Словарь с заголовком Authorization, если токен получен, иначе пустой словарь.
    """
    if os.getenv('DJANGO_REST_ENABLED', 'false').lower() == 'true':
        response = requests.post(
            f"{os.getenv('DJANGOREST_URL')}/auth/token/",
            data={'username': 'test', 'password': 'test'}
        )
        if response.status_code == 200:
            token = response.json().get('access')
            return {'Authorization': f'Bearer {token}'}
        return {}
    return {}


def index(request):
    """Отображает главную страницу с списком всех документов.

    Args:
        request: HTTP-запрос.

    Returns:
        HttpResponse: Рендерит template 'home.html' с данными о документах.
    """
    docs = Docs.objects.all()
    return render(request, 'home.html', {'docs': docs})


def login_view(request):
    """Обрабатывает аутентификацию пользователя и вход в систему.

    Args:
        request: HTTP-запрос.

    Returns:
        HttpResponse: Рендерит template 'login.html' или перенаправляет на главную страницу.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        messages.error(request, 'Неверное имя пользователя или пароль')
    return render(request, 'login.html')


def register(request):
    """Обрабатывает регистрацию нового пользователя.

    Args:
        request: HTTP-запрос.

    Returns:
        HttpResponse: Рендерит template 'register.html' или перенаправляет на главную страницу.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь уже существует')
        else:
            user = User.objects.create_user(username=username, password=password, email=email)
            user.save()
            login(request, user)
            return redirect('index')
    return render(request, 'register.html')


@login_required
def upload_file(request):
    """Обрабатывает загрузку файла пользователем и его сохранение в storage.

    Args:
        request: HTTP-запрос.

    Returns:
        HttpResponse: Рендерит template 'upload.html' или перенаправляет на главную страницу.
    """
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            if not file.name.lower().endswith(('.jpeg', '.jpg', '.png')):
                messages.error(request, 'Неверный формат файла')
                return render(request, 'upload.html', {'form': form})

            file_path = os.path.join(settings.MEDIA_ROOT, file.name)
            with open(file_path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)

            size_kb = os.path.getsize(file_path) / 1024
            doc = Docs.objects.create(file_path=file_path, size=size_kb)
            UsersToDocs.objects.create(username=request.user, docs_id=doc)

            s3 = boto3.client(
                's3',
                endpoint_url=os.getenv('S3_URL'),
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            s3.upload_file(file_path, os.getenv('AWS_STORAGE_BUCKET_NAME'), f"documents/{file.name}")

            base64_data = base64.b64encode(file.read()).decode('utf-8')
            api_url = f"{os.getenv('DJANGOREST_URL')}/proxy/upload_doc/" if os.getenv('DJANGO_REST_ENABLED',
                                                                                      'false').lower() == 'true' else f"{os.getenv('FASTAPI_URL')}/upload_doc/"
            response = requests.post(
                api_url,
                json={'file_data': base64_data, 'file_name': file.name},
                headers=get_api_headers()
            )
            if response.status_code != 201:
                messages.error(request, 'Ошибка загрузки на FastAPI')
                doc.delete()
                return render(request, 'upload.html', {'form': form})

            return redirect('index')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})


@login_required
def delete_doc(request):
    """Обрабатывает удаление документов по их ID (доступно только администраторам и модераторам).

    Args:
        request: HTTP-запрос.

    Returns:
        HttpResponse: Рендерит template 'delete.html' или перенаправляет на главную страницу.
    """
    if not (request.user.is_superuser or request.user.groups.filter(name='moderator').exists()):
        messages.error(request, 'Вам сюда нельзя')
        return render(request, 'delete.html', {'form': DeleteDocForm()})

    if request.method == 'POST':
        form = DeleteDocForm(request.POST)
        if form.is_valid():
            doc_ids = [int(id) for id in form.cleaned_data['doc_ids'].split(',') if id.strip().isdigit()]
            api_url = f"{os.getenv('DJANGOREST_URL')}/proxy/doc_delete/" if os.getenv('DJANGO_REST_ENABLED',
                                                                                      'false').lower() == 'true' else f"{os.getenv('FASTAPI_URL')}/doc_delete/"
            for doc_id in doc_ids:
                try:
                    doc = Docs.objects.get(id=doc_id)
                    response = requests.delete(f"{api_url}{doc_id}/", headers=get_api_headers())
                    if response.status_code == 204:
                        doc.delete()
                    else:
                        messages.error(request, f'Ошибка удаления документа {doc_id}')
                except Docs.DoesNotExist:
                    messages.error(request, f'Документ {doc_id} не найден')
            return redirect('index')
    else:
        form = DeleteDocForm()
    return render(request, 'delete.html', {'form': form})


@login_required
def analyse_doc(request):
    """Обрабатывает запрос на анализ документа по его ID.

    Args:
        request: HTTP-запрос.

    Returns:
        HttpResponse: Рендерит template 'analyse.html' с результатом анализа.
    """
    if request.method == 'POST':
        form = AnalyseDocForm(request.POST)
        if form.is_valid():
            doc_id = form.cleaned_data['doc_id']
            api_url = f"{os.getenv('DJANGOREST_URL')}/proxy/doc_analyse/" if os.getenv('DJANGO_REST_ENABLED',
                                                                                       'false').lower() == 'true' else f"{os.getenv('FASTAPI_URL')}/doc_analyse/"
            response = requests.post(f"{api_url}{doc_id}/", headers=get_api_headers())
            if response.status_code == 200:
                return render(request, 'analyse.html', {'form': form, 'status': response.json().get('status')})
            messages.error(request, 'Ошибка анализа документа')
    else:
        form = AnalyseDocForm()
    return render(request, 'analyse.html', {'form': form})


@login_required
def get_text(request):
    """Извлекает текст из документа по его ID, если пользователь оплатил доступ.

    Args:
        request: HTTP-запрос.

    Returns:
        HttpResponse: Рендерит template 'get_text.html' с извлеченным текстом.
    """
    if request.method == 'POST':
        form = GetTextForm(request.POST)
        if form.is_valid():
            doc_id = form.cleaned_data['doc_id']
            cart = Cart.objects.filter(user_id=request.user, docs_id_id=doc_id).first()
            if not request.user.is_superuser and (not cart or not cart.payment):
                messages.error(request, 'Требуется оплата для доступа к тексту')
                return render(request, 'get_text.html', {'form': form})

            api_url = f"{os.getenv('DJANGOREST_URL')}/proxy/get_text/" if os.getenv('DJANGO_REST_ENABLED',
                                                                                    'false').lower() == 'true' else f"{os.getenv('FASTAPI_URL')}/get_text/"
            response = requests.get(f"{api_url}{doc_id}/", headers=get_api_headers())
            if response.status_code == 200:
                return render(request, 'get_text.html', {'form': form, 'text': response.json().get('text')})
            messages.error(request, 'Текст не найден')
    else:
        form = GetTextForm()
    return render(request, 'get_text.html', {'form': form})


@login_required
def cart(request):
    """Управляет корзиной пользователя, добавляя документы и отображая их список.

    Args:
        request: HTTP-запрос.

    Returns:
        HttpResponse: Рендерит template 'cart.html' с содержимым корзины.
    """
    if request.method == 'POST':
        doc_id = request.POST.get('doc_id')
        try:
            doc = Docs.objects.get(id=doc_id)
            file_type = doc.file_path.split('.')[-1].lower()
            price = Price.objects.get(file_type=file_type)
            order_price = price.price * doc.size
            Cart.objects.create(user_id=request.user, docs_id=doc, order_price=order_price, payment=False)
            messages.success(request, 'Документ добавлен в корзину')
        except (Docs.DoesNotExist, Price.DoesNotExist):
            messages.error(request, 'Ошибка добавления в корзину')
        return redirect('cart')

    carts = Cart.objects.filter(user_id=request.user)
    return render(request, 'cart.html', {'carts': carts})


@login_required
def payment(request):
    """Обрабатывает оплату документов в корзине пользователя.

    Args:
        request: HTTP-запрос.

    Returns:
        HttpResponse: Рендерит template 'payment.html' или перенаправляет на страницу получения текста.
    """
    if request.method == 'POST':
        cart_id = request.POST.get('cart_id')
        try:
            cart = Cart.objects.get(id=cart_id, user_id=request.user)
            if not request.user.is_superuser:
                cart.payment = True
                cart.save()
            messages.success(request, 'Оплата прошла успешно')
            return redirect('get_text')
        except Cart.DoesNotExist:
            messages.error(request, 'Корзина не найдена')
    carts = Cart.objects.filter(user_id=request.user, payment=False)
    return render(request, 'payment.html', {'carts': carts})
