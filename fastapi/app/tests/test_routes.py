import pytest
from app.models import Document, DocumentText
from datetime import date
import os
from unittest.mock import patch

TEST_IMAGE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../NET/fastapi/app/tests/image.jpg")
)

class TestDocumentRoutes:
    def test_upload_document(self, test_client, db_session, test_image):
        # Проверяем что тестовое изображение существует
        assert os.path.exists(TEST_IMAGE_PATH), f"Test image not found at {TEST_IMAGE_PATH}"
        
        # Мокаем Celery task
        with patch('app.tasks.process_document.delay') as mock_process:
            with open(TEST_IMAGE_PATH, 'rb') as f:
                response = test_client.post(
                    "/api/v1/documents/upload",
                    files={"file": ("test_image.jpg", f, "image/jpeg")}
                )
            
            assert response.status_code == 200
            data = response.json()
            assert data['status'] == 'pending'
            assert data['path'].endswith('test_image.jpg')
            
            # Проверяем что документ сохранился в БД
            doc = db_session.query(Document).first()
            assert doc is not None
            assert doc.path.endswith('test_image.jpg')
            
            # Проверяем что задача на обработку была запущена
            mock_process.assert_called_once_with(doc.id)

    def test_get_document_texts(self, test_client, db_session, test_image):
        # Создаем тестовые данные
        doc = Document(
            path=TEST_IMAGE_PATH,
            date=date.today(),
            status="processed"
        )
        db_session.add(doc)
        db_session.commit()
        
        text = DocumentText(
            id_doc=doc.id,
            text="Sample text from OCR"
        )
        db_session.add(text)
        db_session.commit()
        
        # Получаем тексты документа
        response = test_client.get(f"/api/v1/documents/{doc.id}/texts")
        assert response.status_code == 200
        texts = response.json()
        assert len(texts) == 1
        assert texts[0]['text'] == "Sample text from OCR"

    def test_process_document(self, test_client, db_session, test_image):
        # Создаем тестовый документ
        doc = Document(
            path=TEST_IMAGE_PATH,
            date=date.today(),
            status="pending"
        )
        db_session.add(doc)
        db_session.commit()
        
        # Мокаем Celery
        with patch('app.tasks.process_document.delay') as mock_process:
            response = test_client.post(f"/api/v1/documents/{doc.id}/process")
            
            assert response.status_code == 200
            assert response.json() == {
                "status": "processing started",
                "document_id": doc.id
            }
            mock_process.assert_called_once_with(doc.id)

    def test_document_not_found(self, test_client):
        response = test_client.get("/api/v1/documents/999")
        assert response.status_code == 404
        assert "Document not found" in response.json()['detail']
