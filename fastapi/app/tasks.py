from celery import Celery
from app.database import SessionLocal
from app.models import Document, DocumentText
import pytesseract
from PIL import Image
import os
from app.config import settings

app = Celery(
    'tasks',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

app.conf.update(
    broker_url=settings.CELERY_BROKER_URL,
    result_backend=settings.CELERY_RESULT_BACKEND,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    broker_connection_retry_on_startup=True
)

@app.task(bind=True, max_retries=3)
def process_document(self, document_id: int):
    db = SessionLocal()
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise self.retry(countdown=60, max_retries=3)

        document.status = 'processing'
        db.commit()

        try:
            if not os.path.exists(document.path):
                raise FileNotFoundError(f"Document file not found: {document.path}")
            
            image = Image.open(document.path)
            text = pytesseract.image_to_string(image, lang='rus+eng')
            
            db_text = DocumentText(id_doc=document.id, text=text)
            db.add(db_text)
            
            document.status = 'processed'
            db.commit()
            
            return {
                "status": "success",
                "document_id": document_id,
                "text_length": len(text)
            }
            
        except Exception as e:
            document.status = f'error: {str(e)}'
            db.commit()
            raise self.retry(exc=e, countdown=60)
            
    finally:
        db.close()
