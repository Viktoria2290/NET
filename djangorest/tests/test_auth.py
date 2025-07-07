import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def user():
    return User.objects.create_user(username='test', password='test')

@pytest.mark.django_db
def test_token_obtain_pair(client, user):
    response = client.post(reverse('token_obtain_pair'), {'username': 'test', 'password': 'test'})
    assert response.status_code == 200
    assert 'access' in response.json()
    assert 'refresh' in response.json()

@pytest.mark.django_db
def test_token_refresh(client, user):
    token_response = client.post(reverse('token_obtain_pair'), {'username': 'test', 'password': 'test'})
    refresh_token = token_response.json()['refresh']
    response = client.post(reverse('token_refresh'), {'refresh': refresh_token})
    assert response.status_code == 200
    assert 'access' in response.json()
