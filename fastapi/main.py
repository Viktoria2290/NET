from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import base64
import os
import requests
from deps import get_db
from crud import create_document, get_document_text
from tasks import process_document
from typing import List

app = FastAPI()


class DocumentUpload(BaseModel):
    file_data: str
    file_name: str


@app.post("/upload_doc")
async def upload_doc(docs: List[DocumentUpload], db: Session = Depends(get_db)):
    try:
        uploaded_docs = []
        for doc in docs:
            if not doc.file_name.lower().endswith(('.jpeg', '.jpg', '.png')):
                raise HTTPException(status_code=400, detail="Invalid file format")

            file_data = base64.b64decode(doc.file_data)
            file_path = f"/app/documents/{doc.file_name}"
            with open(file_path, "wb") as f:
                f.write(file_data)

            doc_id = create_document(db, file_path)
            process_document.delay(doc_id, file_path)

            if os.getenv("DJANGO_REST_ENABLED") == "true":
                response = requests.post(
                    f"{os.getenv('DJANGOREST_URL')}/s3/upload/",
                    json={"file_path": file_path, "doc_id": doc_id}
                )
                if response.status_code != 200:
                    raise HTTPException(status_code=500, detail="Failed to upload to S3")

            uploaded_docs.append({"id": doc_id, "file_path": file_path})

        return uploaded_docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_text/{doc_id}")
async def get_text(doc_id: int, db: Session = Depends(get_db)):
    text = get_document_text(db, doc_id)
    if not text:
        raise HTTPException(status_code=404, detail="Text not found")
    return {"id": doc_id, "text": text}


@app.get("/docs")
async def docs():
    return {"message": "Swagger UI available at /docs"}
