from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Chunk, Document


router = APIRouter()


@router.get("")
def list_documents(db: Session = Depends(get_db)):
    rows = (
        db.query(Document, func.count(Chunk.id).label("chunk_count"))
        .outerjoin(Chunk, Chunk.document_id == Document.id)
        .group_by(Document.id)
        .order_by(Document.created_at.desc())
        .all()
    )
    return [
        {
            "id": str(doc.id),
            "title": doc.title,
            "source": doc.source,
            "chunks": count,
            "created_at": doc.created_at.isoformat(),
        }
        for doc, count in rows
    ]


@router.delete("/{document_id}")
def delete_document(document_id: UUID, db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    db.delete(doc)
    db.commit()
    return {"deleted": str(document_id)}
