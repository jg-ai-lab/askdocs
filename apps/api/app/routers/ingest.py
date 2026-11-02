from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Chunk, Document
from app.services.chunking import chunk_text
from app.services.embeddings import embed_batch
from app.services.storage import upload_pdf


router = APIRouter()


@router.post("")
async def ingest_pdf(file: UploadFile, db: Session = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF uploads are supported in this scaffold.")

    raw_bytes = await file.read()
    object_key = upload_pdf(raw_bytes, file.filename)

    reader = PdfReader(BytesIO(raw_bytes))
    raw = "\n\n".join((page.extract_text() or "") for page in reader.pages)
    chunks = chunk_text(raw)
    if not chunks:
        raise HTTPException(400, "No extractable text in PDF.")

    embeddings = embed_batch(chunks)

    doc = Document(title=file.filename, source=f"s3://{object_key}")
    db.add(doc)
    db.flush()

    db.add_all(
        Chunk(document_id=doc.id, position=i, content=c, embedding=e)
        for i, (c, e) in enumerate(zip(chunks, embeddings))
    )
    db.commit()
    return {"document_id": str(doc.id), "chunks": len(chunks), "object_key": object_key}
