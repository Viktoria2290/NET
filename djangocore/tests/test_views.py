import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User
from .models import Docs, UsersToDocs, Price, Cart
import os

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass')

@pytest.mark.django_db
def test_index_view(client):
    response = client.get(reverse('index'))
    assert response.status_code == 200
    assert 'Добро пожаловать в DocMagic' in str(response.content)

@pytest.mark.django_db
def test_login_view(client):
    response = client.post(reverse('login'), {'username': 'test', 'password': 'test'})
    assert response.status_code == 302

@pytest.mark.django_db
def test_register_view(client):
    response = client.post(reverse('register'), {'username': 'newuser', 'password': 'newpass', 'email': 'new@example.com'})
    assert response.status_code == 302
    assert User.objects.filter(username='newuser').exists()

@pytest.mark.django_db
def test_upload_file_view(client, user):
    client.login(username='testuser', password='testpass')
    with open('/NET/djangocore/media/test.jpg', 'wb') as f:
        f.write(b'fake image data')
    with open('/NET/djangocore/media/test.jpg', 'rb') as f:
        response = client.post(reverse('upload_file'), {'file': f})
    assert response.status_code == 302
    assert Docs.objects.count() == 1

@pytest.mark.django_db
def test_delete_doc_view(client, user):
    client.login(username='test', password='test')
    doc = Docs.objects.create(file_path='/media/test.jpg', size=5.0)
    response = client.post(reverse('delete_doc'), {'doc_ids': str(doc.id)})
    assert response.status_code == 302
    assert not Docs.objects.filter(id=doc.id).exists()

@pytest.mark.django_db
def test_analyse_doc_view(client, user):
    client.login(username='testuser', password='testpass')
    response = client.post(reverse('analyse_doc'), {'doc_id': 1})
    assert response.status_code == 200

@pytest.mark.django_db
def test_get_text_view(client, user):
    client.login(username='test', password='test')
    doc = Docs.objects.create(file_path='/media/test.jpg', size=5.0)
    Cart.objects.create(user_id=user, docs_id=doc, order_price=100.0, payment=True)
    response = client.post(reverse('get_text'), {'doc_id': doc.id})
    assert response.status_code == 200

@pytest.mark.django_db
def test_cart_view(client, user):
    client.login(username='testuser', password='testpass')
    doc = Docs.objects.create(file_path='/media/test.jpg', size=5.0)
    Price.objects.create(file_type='jpg', price=2.0)
    response = client.post(reverse('cart'), {'doc_id': doc.id})
    assert response.status_code == 302
    assert Cart.objects.count() == 1

@pytest.mark.django_db
def test_payment_view(client, user):
    client.login(username='testuser', password='testpass')
    doc = Docs.objects.create(file_path='/media/test.jpg', size=5.0)
    cart = Cart.objects.create(user_id=user, docs_id=doc, order_price=100.0, payment=False)
    response = client.post(reverse('payment'), {'cart_id': cart.id})
    assert response.status_code == 302
    cart.refresh_from_db()
    assert cart.payment == True
