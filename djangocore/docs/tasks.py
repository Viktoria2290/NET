from celery import Celery
from django.conf import settings
import pytesseract
import os
from PIL import Image

app = Celery('docs', broker=settings.CELERY_BROKER_URL, backend='rpc://')
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@app.task
def process_document(document_id):
    from .models import Docs
    document = Docs.objects.get(id=document_id)
    file_path = document.file_path
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image, lang='rus+eng')
        document.text = text
        document.status = 'обработан'
    except Exception as e:
        document.status = 'ошибка'
        document.text = f'Ошибка обработки: {str(e)}'
    document.save()
