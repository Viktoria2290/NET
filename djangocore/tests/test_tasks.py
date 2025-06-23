import pytest
from docs.tasks import process_document
from docs.models import Docs

@pytest.mark.django_db
def test_process_document_task(mocker):
    # Мокируем pytesseract, чтобы не зависеть от реального OCR
    mocker.patch("pytesseract.image_to_string", return_value="Mocked text")
    
    doc = Docs.objects.create(file_path="test.jpg", status="новый")
    process_document(doc.id)
    
    updated_doc = Docs.objects.get(id=doc.id)
    assert updated_doc.status == "обработан"
    assert updated_doc.text == "Mocked text"
