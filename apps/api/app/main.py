from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.db import Base, engine
from app.routers import documents, ingest, query, stats


MIGRATIONS = [
    "CREATE EXTENSION IF NOT EXISTS vector",
    "ALTER TABLE chunks ADD COLUMN IF NOT EXISTS content_tsv tsvector "
    "GENERATED ALWAYS AS (to_tsvector('english', content)) STORED",
    "CREATE INDEX IF NOT EXISTS idx_chunks_content_tsv "
    "ON chunks USING gin(content_tsv)",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        for stmt in MIGRATIONS:
            conn.execute(text(stmt))
    yield


app = FastAPI(title="DocuChat API", version="0.3.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
app.include_router(query.router, prefix="/query", tags=["query"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(stats.router, prefix="/stats", tags=["stats"])
