import pytest
from app.tasks import process_document
from app.crud import Document, DocumentText
from app.deps import get_db

def test_process_document():
    db = next(get_db())
    doc = Document(file_path="/app/documents/test.jpg")
    db.add(doc)
    db.commit()
    process_document(doc.id, "/app/documents/test.jpg")
    text = db.query(DocumentText).filter(DocumentText.document_id == doc.id).first()
    assert text is not None
