import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass')

def test_token_obtain_pair(client, user):
    url = reverse('token_obtain_pair')
    response = client.post(url, {'username': 'testuser', 'password': 'testpass'})
    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data

def test_token_obtain_pair_invalid(client):
    url = reverse('token_obtain_pair')
    response = client.post(url, {'username': 'wronguser', 'password': 'wrongpass'})
    assert response.status_code == 401
    assert 'detail' in response.data

def test_token_refresh(client, user):
    token_url = reverse('token_obtain_pair')
    token_response = client.post(token_url, {'username': 'testuser', 'password': 'testpass'})
    refresh_token = token_response.data['refresh']
    url = reverse('token_refresh')
    response = client.post(url, {'refresh': refresh_token})
    assert response.status_code == 200
    assert 'access' in response.data

def test_token_refresh_invalid(client):
    url = reverse('token_refresh')
    response = client.post(url, {'refresh': 'invalid_token'})
    assert response.status_code == 401
    assert 'detail' in response.data
