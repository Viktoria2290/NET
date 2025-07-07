import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_doc():
    response = client.post("/upload_doc", json=[{"file_data": "data:image/jpeg;base64,/9j/4AAQSkZJRg==", "file_name": "test.jpg"}])
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert "id" in response.json()[0]

def test_get_text_not_found():
    response = client.get("/get_text/999")
    assert response.status_code == 404
