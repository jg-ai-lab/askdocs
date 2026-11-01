"""Hybrid retrieval: vector cosine + BM25-style full-text search, merged with RRF.

Reciprocal Rank Fusion is simple and surprisingly hard to beat on mixed
corpora. It needs no tuning (constant k=60) and only cares about ranks,
so vector cosine distance and ts_rank can be fused without normalization.

Reference: Cormack, Clarke, Buettcher (2009).
"""
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Chunk


RRF_K = 60


def _vector_ids(db: Session, q_emb: list[float], limit: int) -> list[UUID]:
    rows = (
        db.query(Chunk.id)
        .order_by(Chunk.embedding.cosine_distance(q_emb))
        .limit(limit)
        .all()
    )
    return [row[0] for row in rows]


def _fulltext_ids(db: Session, question: str, limit: int) -> list[UUID]:
    rows = db.execute(
        text(
            """
            SELECT id
            FROM chunks
            WHERE content_tsv @@ websearch_to_tsquery('english', :q)
            ORDER BY ts_rank(content_tsv, websearch_to_tsquery('english', :q)) DESC
            LIMIT :k
            """
        ),
        {"q": question, "k": limit},
    ).scalars().all()
    return list(rows)


def _rrf_merge(*ranked_lists: list[UUID]) -> list[UUID]:
    scores: dict[UUID, float] = {}
    for ranked in ranked_lists:
        for rank, chunk_id in enumerate(ranked):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (RRF_K + rank)
    return sorted(scores, key=lambda cid: scores[cid], reverse=True)


def hybrid_search(db: Session, question: str, q_emb: list[float]) -> list[Chunk]:
    """Return top-K chunks fused from vector + full-text ranks."""
    pool = settings.top_k * 4

    vec = _vector_ids(db, q_emb, pool)
    ft = _fulltext_ids(db, question, pool)

    if not ft:
        # Fall back to pure vector when FT finds nothing — common for very
        # short questions or non-English queries not matching ts config.
        ordered = vec
    else:
        ordered = _rrf_merge(vec, ft)

    top_ids = ordered[: settings.top_k]
    if not top_ids:
        return []

    chunks = db.query(Chunk).filter(Chunk.id.in_(top_ids)).all()
    by_id = {c.id: c for c in chunks}
    return [by_id[cid] for cid in top_ids if cid in by_id]
