import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User
import boto3
from botocore.stub import Stubber

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def user():
    return User.objects.create_user(username='test', password='test')

@pytest.mark.django_db
def test_s3_get_view(client, user):
    client.login(username='test', password='test')
    token_response = client.post(reverse('token_obtain_pair'), {'username': 'test', 'password': 'test'})
    token = token_response.json()['access']
    
    s3 = boto3.client('s3', endpoint_url='https://s3.ru1.storage.beget.cloud')
    stubber = Stubber(s3)
    stubber.add_response('get_object', {'Body': b'test data'})
    stubber.activate()
    
    response = client.get(reverse('s3_get'), {'doc_id': 'test.jpg'}, HTTP_AUTHORIZATION=f'Bearer {token}')
    assert response.status_code == 200
    assert response.json()['content'] == 'test data'
