import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from unittest.mock import patch
from io import BytesIO

@pytest.mark.django_db
@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass')

@pytest.fixture
def auth_client(client, user):
    token_url = reverse('token_obtain_pair')
    response = client.post(token_url, {'username': 'testuser', 'password': 'testpass'})
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')
    return client

@patch('logger.views.Session')
def test_s3_get_success(mock_session, auth_client):
    mock_s3 = mock_session.return_value.client.return_value
    mock_s3.get_object.return_value = {'Body': BytesIO(b'test content')}
    url = reverse('s3_get')
    response = auth_client.get(url, {'file_id': 'test_file'})
    assert response.status_code == 200
    assert response.data['file'] == 'test content'
    mock_s3.get_object.assert_called_with(Bucket='142c8736a6df-neglectful-dogmeat', Key='test_file')

@patch('logger.views.Session')
def test_s3_get_not_found(mock_session, auth_client):
    mock_s3 = mock_session.return_value.client.return_value
    mock_s3.get_object.side_effect = Exception('Not found')
    url = reverse('s3_get')
    response = auth_client.get(url, {'file_id': 'invalid_file'})
    assert response.status_code == 404
    assert 'error' in response.data

@patch('logger.views.Session')
def test_s3_delete_success(mock_session, auth_client):
    mock_s3 = mock_session.return_value.client.return_value
    mock_s3.delete_object.return_value = {}
    url = reverse('s3_delete')
    response = auth_client.delete(url, {'file_id': 'test_file'})
    assert response.status_code == 200
    assert response.data['message'] == 'File deleted'
    mock_s3.delete_object.assert_called_with(Bucket='142c8736a6df-neglectful-dogmeat', Key='test_file')

@patch('logger.views.Session')
def test_s3_delete_not_found(mock_session, auth_client):
    mock_s3 = mock_session.return_value.client.return_value
    mock_s3.delete_object.side_effect = Exception('Not found')
    url = reverse('s3_delete')
    response = auth_client.delete(url, {'file_id': 'invalid_file'})
    assert response.status_code == 404
    assert 'error' in response.data

@patch('middleware.s3.Session')
def test_s3_middleware_upload_success(mock_session, auth_client):
    mock_s3 = mock_session.return_value.client.return_value
    mock_s3.upload_fileobj.return_value = None
    url = reverse('proxy')
    file = BytesIO(b'test content')
    response = auth_client.post(url, {'file': file}, format='multipart')
    assert response.status_code == 200
    mock_s3.upload_fileobj.assert_called()
