from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import Chunk
from app.services.embeddings import embed_one
from app.services.llm import stream_answer


router = APIRouter()


class QueryRequest(BaseModel):
    question: str


@router.post("")
def query(req: QueryRequest, db: Session = Depends(get_db)):
    q_emb = embed_one(req.question)
    rows = (
        db.query(Chunk)
        .order_by(Chunk.embedding.cosine_distance(q_emb))
        .limit(settings.top_k)
        .all()
    )
    context = [{"id": str(c.id), "content": c.content, "doc_id": str(c.document_id)} for c in rows]
    return StreamingResponse(stream_answer(req.question, context), media_type="text/event-stream")
