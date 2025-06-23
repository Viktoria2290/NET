import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from docs.models import Docs, Cart

@pytest.mark.django_db
def test_index_view(client):
    response = client.get(reverse("index"))
    assert response.status_code == 200

@pytest.mark.django_db
def test_login_view(client):
    User.objects.create_user(username="testuser", password="testpass")
    response = client.post(reverse("login"), {"username": "testuser", "password": "testpass"})
    assert response.status_code == 302  # Redirect after login

@pytest.mark.django_db
def test_upload_view_authenticated(admin_client):
    response = admin_client.get(reverse("upload"))
    assert response.status_code == 200

@pytest.mark.django_db
def test_document_list_view(admin_client):
    Docs.objects.create(file_path="/uploads/test.jpg", size=1024)
    response = admin_client.get(reverse("documents"))
    assert response.status_code == 200
    assert "docs" in response.context
