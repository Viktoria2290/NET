from celery import Celery
from sqlalchemy.orm import Session
from fastapi.app.deps import get_db
from fastapi.app.crud import DocumentText
import requests
import os

app = Celery('tasks', broker='amqp://guest@rabbitmq:5672//', backend='redis://redis:6379/0')

@app.task
def process_document(doc_id: int, file_path: str):
    db = next(get_db())
    try:
        with open(file_path, "rb") as f:
            response = requests.post(
                "http://tesseract:8080/ocr",
                files={"file": f}
            )
        if response.status_code == 200:
            text = response.json().get("text")
            doc_text = DocumentText(document_id=doc_id, text=text)
            db.add(doc_text)
            db.commit()
    except Exception as e:
        db.rollback()
        raise e
