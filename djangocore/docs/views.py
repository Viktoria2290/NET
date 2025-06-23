from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from .models import Docs, UsersToDocs, Price, Cart
from .forms import DocumentForm
import httpx
import os
import json
from datetime import datetime
import requests

def is_moderator(user):
    return user.is_staff or user.is_superuser

def make_request(method, endpoint, data=None, files=None, headers=None):
    """Helper function to handle requests to FastAPI or DjangoREST"""
    fastapi_url = f"{settings.FASTAPI_URL}{endpoint}"
    djangorest_url = f"{settings.DJANGOREST_URL}/proxy{endpoint}"
    url = djangorest_url if settings.DJANGO_REST_ENABLED else fastapi_url
    if settings.DJANGO_REST_ENABLED:
        try:
            response = requests.post(
                f"{settings.DJANGOREST_URL}/auth/token",
                data={'username': 'test', 'password': 'test'}
            )
            if response.status_code == 200:
                token = response.json()['access']
                headers = headers or {}
                headers['Authorization'] = f'Bearer {token}'
        except requests.RequestException as e:
            messages.error(None, f'Ошибка получения токена: {str(e)}')
            return None
    try:
        if method == 'POST':
            response = requests.post(url, json=data, files=files, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        elif method == 'GET':
            response = requests.get(url, headers=headers)
        return response
    except requests.RequestException as e:
        messages.error(None, f'Ошибка запроса: {str(e)}')
        return None

def index(request):
    docs = Docs.objects.all()
    return render(request, 'docs/index.html', {'docs': docs})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Неверные данные')
    return render(request, 'docs/login.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Ошибка регистрации')
    else:
        form = UserCreationForm()
    return render(request, 'docs/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def upload_view(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        valid_extensions = ['jpeg', 'jpg', 'png']
        for file in files:
            ext = file.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                messages.error(request, f'Недопустимый формат: {file.name}')
                continue
            file_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.name}"
            file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                f.write(file.read())
            size_kb = file.size / 1024
            doc = Docs.objects.create(file_path=file_path, size=size_kb)
            UsersToDocs.objects.create(username=request.user.username, docs=doc)
            price = Price.objects.filter(file_type=ext).first()
            if price:
                Cart.objects.create(user=request.user, docs=doc, order_price=size_kb * price.price)
            response = make_request('POST', '/api/upload_doc', files={'file': (file_name, open(file_path, 'rb'), f'image/{ext}')})
            if not response or response.status_code != 200:
                messages.error(request, f'Ошибка загрузки {file_name}: FastAPI вернул {response.status_code if response else "недоступен"}')
        return redirect('documents')
    return render(request, 'docs/upload.html')

@login_required
def document_list(request):
    docs = Docs.objects.all()
    return render(request, 'docs/document_list.html', {'docs': docs})

@login_required
@user_passes_test(is_moderator)
def delete_view(request):
    if request.method == 'POST':
        doc_ids = request.POST.get('doc_ids').split(',')
        for doc_id in doc_ids:
            try:
                doc = Docs.objects.get(id=doc_id)
                response = make_request('DELETE', f'/api/delete/{doc_id}')
                if response and response.status_code == 200:
                    doc.delete()
                    messages.success(request, f'Документ {doc_id} удален')
                else:
                    messages.error(request, f'Ошибка удаления документа {doc_id}')
            except Docs.DoesNotExist:
                messages.error(request, f'Документ {doc_id} не найден')
        return redirect('documents')
    return render(request, 'docs/delete.html')

@login_required
def analyse_view(request):
    if request.method == 'POST':
        doc_id = request.POST.get('doc_id')
        try:
            doc = Docs.objects.get(id=doc_id)
            response = make_request('POST', '/api/analyse', data={'id': doc_id})
            if response and response.status_code == 200:
                return JsonResponse({'status': 'Анализ начат', 'doc_id': doc_id})
            else:
                return JsonResponse({'status': 'Ошибка анализа'}, status=400)
        except Docs.DoesNotExist:
            return JsonResponse({'status': 'Документ не найден'}, status=404)
    docs = Docs.objects.all()
    return render(request, 'docs/analyse.html', {'docs': docs})

@login_required
def get_text(request, doc_id):
    try:
        doc = Docs.objects.get(id=doc_id)
        cart = Cart.objects.filter(user=request.user, docs=doc, payment=True).first()
        if cart or request.user.is_staff or request.user.is_superuser:
            response = make_request('GET', f'/api/text/{doc_id}')
            if response and response.status_code == 200:
                text = response.json().get('text', doc.text)
                return render(request, 'docs/text.html', {'doc': doc, 'text': text})
        return redirect('cart')
    except Docs.DoesNotExist:
        messages.error(request, 'Документ не найден')
        return redirect('documents')

@login_required
def cart_view(request):
    carts = Cart.objects.filter(user=request.user)
    return render(request, 'docs/cart.html', {'carts': carts})

@login_required
def payment_view(request, cart_id):
    try:
        cart = Cart.objects.get(id=cart_id, user=request.user)
        if request.method == 'POST':
            card_number = request.POST.get('card_number')
            if card_number:  # Простая проверка для демонстрации
                cart.payment = True
                cart.save()
                messages.success(request, 'Оплата прошла успешно')
                return redirect('documents')
            else:
                messages.error(request, 'Ошибка оплаты')
        return render(request, 'docs/payment.html', {'cart': cart})
    except Cart.DoesNotExist:
        messages.error(request, 'Корзина не найдена')
        return redirect('cart')

@login_required
def upload_doc_api(request):
    if request.method == 'POST':
        file = request.FILES.get('file_path')
        if file:
            ext = file.name.split('.')[-1].lower()
            valid_extensions = ['jpeg', 'jpg', 'png']
            if ext not in valid_extensions:
                return JsonResponse({'error': 'Недопустимый формат файла'}, status=400)
            file_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.name}"
            file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                f.write(file.read())
            size_kb = file.size / 1024
            doc = Docs.objects.create(file_path=file_path, size=size_kb)
            UsersToDocs.objects.create(username=request.user.username, docs=doc)
            price = Price.objects.filter(file_type=ext).first()
            if price:
                Cart.objects.create(user=request.user, docs=doc, order_price=size_kb * price.price)
            return JsonResponse({'status': 'Документ загружен', 'doc_id': doc.id})
        return JsonResponse({'error': 'Файл не предоставлен'}, status=400)
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

@login_required
@user_passes_test(is_moderator)
def doc_delete_api(request, doc_id):
    if request.method == 'DELETE':
        try:
            doc = Docs.objects.get(id=doc_id)
            doc.delete()
            return JsonResponse({'status': 'Документ удален'})
        except Docs.DoesNotExist:
            return JsonResponse({'error': 'Документ не найден'}, status=404)
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

@login_required
def doc_analyse_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        doc_id = data.get('id')
        try:
            doc = Docs.objects.get(id=doc_id)
            from .tasks import process_document
            process_document.delay(doc_id)
            return JsonResponse({'status': 'Анализ начат', 'doc_id': doc_id})
        except Docs.DoesNotExist:
            return JsonResponse({'error': 'Документ не найден'}, status=404)
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

@login_required
def get_text_api(request, doc_id):
    try:
        doc = Docs.objects.get(id=doc_id)
        cart = Cart.objects.filter(user=request.user, docs=doc, payment=True).first()
        if cart or request.user.is_staff or request.user.is_superuser:
            return JsonResponse({'text': doc.text})
        return JsonResponse({'error': 'Оплата требуется'}, status=403)
    except Docs.DoesNotExist:
        return JsonResponse({'error': 'Документ не найден'}, status=404)
