import pytest
from django.urls import reverse
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_upload_doc_api(admin_client):
    with open("test.jpg", "rb") as f:
        response = admin_client.post(
            reverse("upload_doc_api"),
            {"file_path": f},
            format="multipart"
        )
    assert response.status_code == 200
    assert "doc_id" in response.json()

@pytest.mark.django_db
def test_get_text_api(admin_client):
    doc = Docs.objects.create(file_path="test.jpg", text="Sample text")
    response = admin_client.get(reverse("get_text_api", args=[doc.id]))
    assert response.status_code == 200
    assert response.json()["text"] == "Sample text"
