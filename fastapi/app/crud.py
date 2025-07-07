from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    file_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class DocumentText(Base):
    __tablename__ = "documents_text"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer)
    text = Column(String)

def create_document(db: Session, file_path: str):
    doc = Document(file_path=file_path)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc.id

def get_document_text(db: Session, document_id: int):
    text = db.query(DocumentText).filter(DocumentText.document_id == document_id).first()
    return text.text if text else None
