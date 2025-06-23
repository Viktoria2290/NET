from pydantic import BaseModel
from datetime import date
from typing import List, Optional

class DocumentBase(BaseModel):
    path: str
    date: date

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: int
    status: str
    texts: List['DocumentText'] = []

    class Config:
        from_attributes = True

class DocumentTextBase(BaseModel):
    id_doc: int
    text: str

class DocumentTextCreate(DocumentTextBase):
    pass

class DocumentText(DocumentTextBase):
    id: int
    document: Optional[Document] = None

    class Config:
        from_attributes = True
