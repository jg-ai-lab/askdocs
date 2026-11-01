from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import QueryLog


router = APIRouter()


EMBEDDING_COST_PER_1K = 0.00002
HAIKU_IN_COST_PER_1M = 1.00
HAIKU_OUT_COST_PER_1M = 5.00


def _estimated_cost(input_tokens: int, output_tokens: int) -> float:
    return (
        input_tokens / 1_000_000 * HAIKU_IN_COST_PER_1M
        + output_tokens / 1_000_000 * HAIKU_OUT_COST_PER_1M
    )


@router.get("")
def stats(db: Session = Depends(get_db)):
    row = db.query(
        func.count(QueryLog.id),
        func.coalesce(func.avg(QueryLog.latency_ms), 0.0),
        func.coalesce(func.sum(QueryLog.input_tokens), 0),
        func.coalesce(func.sum(QueryLog.output_tokens), 0),
    ).one()
    count, avg_latency, in_tokens, out_tokens = row
    return {
        "query_count": int(count),
        "avg_latency_ms": round(float(avg_latency), 1),
        "total_input_tokens": int(in_tokens),
        "total_output_tokens": int(out_tokens),
        "estimated_cost_usd": round(_estimated_cost(int(in_tokens), int(out_tokens)), 4),
    }
