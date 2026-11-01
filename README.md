# DocuChat

> **Status:** In progress — launching next week.

A production-grade RAG chatbot. Upload PDFs or web pages, ask questions in
natural language, get answers with inline citations.

**Live demo:** _coming soon_
**Video walkthrough:** _coming soon_

## Why this exists

Most RAG demos retrieve the wrong chunks and hallucinate confidently.
DocuChat is built to show that retrieval quality, cost, and latency can
be measured and optimized — not left to vibes.

## Stack

| Layer | Tech |
|---|---|
| Frontend | Next.js 14 (App Router), Tailwind, shadcn/ui |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Vector store | PostgreSQL + pgvector |
| Embeddings | OpenAI `text-embedding-3-small` |
| LLM | Anthropic Claude Haiku 4.5 (answers), Claude Sonnet 4.6 (optional reranking) |
| Deployment | Railway (API + DB), Vercel (web) |

## Architecture

```
 User ──► Next.js ──► FastAPI ──► Postgres+pgvector
                         │
                         ├─► Embeddings API (OpenAI)
                         └─► Chat completion (Anthropic Claude)
```

### Retrieval pipeline
1. Document → clean + chunk (recursive, ~500 tokens, 50 overlap)
2. Chunk → embedding → `documents.embedding` column
3. Query → embedding → **hybrid search** (cosine similarity + BM25)
4. Top-k chunks → rerank → context window
5. LLM call with inline-citation prompt → stream to client

## Target metrics (will be measured, not claimed)

- Retrieval top-3 hit rate: **≥ 85%** on 50-question eval set
- Avg cost per query: **< $0.005**
- p95 end-to-end latency: **< 2.0s**
- Streaming TTFT: **< 500ms**

## Roadmap

- [x] Day 1: Repo + Postgres+pgvector + ingest pipeline
- [x] Day 2: `/ingest` + `/query` endpoints, cosine retrieval
- [x] Day 3: Next.js UI + streaming (SSE)
- [x] Day 4: Admin dashboard (docs list, upload, stats) + query logging
- [x] Day 5: Dockerfile + Railway config + eval harness scaffold
- [ ] Day 6: Hybrid search (BM25 + vector), citation UI polish
- [ ] Day 7: Deploy + custom domain + demo video + eval run on real corpus

## Local development

```bash
# 1. Infrastructure
docker compose up -d

# 2. Backend
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in API keys
uvicorn app.main:app --reload

# 3. Frontend
cd apps/web
pnpm install
pnpm dev
```

## License

MIT
