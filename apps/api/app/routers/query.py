import json
import time

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.db import SessionLocal, get_db
from app.models import Chunk, QueryLog
from app.services.embeddings import embed_one
from app.services.llm import stream_answer_tracked


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

    def event_stream():
        start = time.perf_counter()
        collected: list[str] = []
        in_tokens = 0
        out_tokens = 0
        for event in stream_answer_tracked(req.question, context):
            if "delta" in event:
                collected.append(event["delta"])
                yield f"data: {json.dumps({'delta': event['delta']})}\n\n".encode()
            elif "usage" in event:
                in_tokens = event["usage"]["input_tokens"]
                out_tokens = event["usage"]["output_tokens"]
        latency_ms = (time.perf_counter() - start) * 1000
        yield (
            f"data: {json.dumps({'done': True, 'sources': [c['id'] for c in context], 'latency_ms': round(latency_ms, 1)})}\n\n"
        ).encode()

        with SessionLocal() as log_db:
            log_db.add(
                QueryLog(
                    question=req.question,
                    answer="".join(collected),
                    source_chunk_ids=",".join(c["id"] for c in context),
                    latency_ms=latency_ms,
                    input_tokens=in_tokens,
                    output_tokens=out_tokens,
                )
            )
            log_db.commit()

    return StreamingResponse(event_stream(), media_type="text/event-stream")
