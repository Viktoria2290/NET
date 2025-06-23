from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Text, Date
from app.database import Base
from datetime import date
from typing import List  # Для аннотации списка отношений

class Document(Base):
    __tablename__ = 'documents'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(String(255))  # Явно указываем тип и длину
    date: Mapped[date] = mapped_column(Date())  # Явно указываем тип Date
    status: Mapped[str] = mapped_column(String(50), default='pending')  # pending, processing, processed, error
    
    texts: Mapped[List["DocumentText"]] = relationship("DocumentText", back_populates="document")

class DocumentText(Base):
    __tablename__ = 'documents_text'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    id_doc: Mapped[int] = mapped_column(ForeignKey('documents.id'))
    text: Mapped[str] = mapped_column(Text())  # Используем Text для больших текстов
    
    document: Mapped["Document"] = relationship("Document", back_populates="texts")
