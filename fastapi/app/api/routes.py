from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Document, DocumentText
from app.schemas import Document as DocumentSchema, DocumentCreate, DocumentText as DocumentTextSchema
from app.tasks import process_document
from typing import List
import os
from datetime import date
import shutil
import uuid

router = APIRouter()

UPLOAD_DIR = "/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/documents/upload", response_model=DocumentSchema)
async def upload_document(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    try:
        # Генерация уникального имени файла
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Сохранение файла
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Создание записи в БД
        db_document = Document(
            path=file_path,
            date=date.today()
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        # Запуск обработки в фоне
        if background_tasks:
            background_tasks.add_task(process_document.delay, db_document.id)
        
        return db_document
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/", response_model=List[DocumentSchema])
async def read_documents(db: Session = Depends(get_db)):
    return db.query(Document).all()

@router.get("/documents/{document_id}", response_model=DocumentSchema)
async def read_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.get("/documents/{document_id}/texts", response_model=List[DocumentTextSchema])
async def read_document_texts(document_id: int, db: Session = Depends(get_db)):
    return db.query(DocumentText).filter(DocumentText.id_doc == document_id).all()

@router.post("/documents/{document_id}/process")
async def trigger_processing(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    process_document.delay(document_id)
    return {"status": "processing started", "document_id": document_id}
