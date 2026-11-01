# askdocs

A production-grade RAG chatbot. Upload PDFs, ask questions in natural
language, get answers with inline citations.

> **Zero-cost by default.** Runs fully local with Ollama (Qwen 2.5 + 
> nomic-embed-text) — no API keys, no cloud bills, no vendor lock-in.
> Optional swap to Anthropic + OpenAI for one-line config.

**Open-source reference project — adaptable to your corpus.**

---

## Why this exists

Most RAG demos retrieve the wrong chunks and hallucinate confidently.
askdocs is built to show that retrieval quality, cost, and latency can
be **measured and optimized** — not left to vibes.

## Features

- **Hybrid search** — BM25 full-text + vector cosine, fused with RRF
- **Inline citations** — every factual claim ends with `[chunk_id]`
- **Hallucination guardrail** — "I don't know" when context is missing
- **Streaming responses** — ChatGPT-style word-by-word UX
- **Admin dashboard** — upload docs, delete, view usage + cost
- **Eval harness** — top-K hit rate on a question set
- **Query logging** — latency, tokens, cost per request
- **Dockerized** — one `docker compose up` for the DB

## Stack

| Layer | Default (local, $0) | Opt-in (cloud, paid) |
|---|---|---|
| LLM | Ollama + Qwen 2.5 7B | Anthropic Claude Haiku 4.5 |
| Embeddings | Ollama + nomic-embed-text | OpenAI text-embedding-3-small |
| Vector DB | Postgres + pgvector | same |
| Full-text | Postgres `tsvector` + GIN | same |
| Backend | FastAPI, SQLAlchemy, Pydantic | same |
| Frontend | Next.js 14, Tailwind | same |

Flip providers via env vars — no code changes required.

## Architecture

```
 User ──► Next.js ──► FastAPI ──► Hybrid retrieval ──► LLM (Ollama / Claude)
                         │              │                      │
                         ▼              ▼                      │
                   Postgres+pgvector   tsvector + BM25         │
                         │                                     │
                         └──── query_logs ◄────────────────────┘
                              (latency, tokens, cost)
```

## Local run — zero API cost (recommended)

**Prerequisites**: Docker, Python 3.12+, Node 18+, [Ollama](https://ollama.com/download)

```bash
# 1. Install the local models (one-time; ~5 GB download)
ollama pull qwen2.5:7b
ollama pull nomic-embed-text

# 2. Start the vector DB
docker compose up -d

# 3. Backend
cd apps/api
python -m venv .venv && source .venv/bin/activate     # (Windows: .\.venv\Scripts\Activate.ps1)
pip install -r requirements.txt
cp .env.example .env     # defaults are already set to Ollama
uvicorn app.main:app --reload

# 4. Frontend (new terminal)
cd apps/web
pnpm install     # or npm install
pnpm dev

# Open http://localhost:3000  (chat)
# Open http://localhost:3000/admin  (upload docs + stats)
```

That's it. No API keys. No bills. Everything runs on your laptop.

### Hardware guidance for the local path

| Setup | Experience |
|---|---|
| 16 GB RAM, Apple Silicon or recent NVIDIA | Smooth, 20–40 tok/s |
| 8 GB RAM, CPU-only | Works with `qwen2.5:3b` instead — change `OLLAMA_LLM_MODEL` |
| < 8 GB RAM | Use `llama3.2:1b` or switch to the cloud path below |

## Cloud path — opt-in (paid)

If you prefer higher-quality responses or want to deploy publicly:

```env
# .env
LLM_PROVIDER=anthropic
EMBEDDING_PROVIDER=openai
EMBEDDING_DIM=1536                        # must match provider!
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

Expected cost at 50 queries/day: **~$7/month**.

See [`DEPLOY_RAILWAY.md`](./DEPLOY_RAILWAY.md) for cloud deployment.

## Roadmap

- [x] Day 1: Repo + Postgres+pgvector + ingest pipeline
- [x] Day 2: `/ingest` + `/query` endpoints, cosine retrieval
- [x] Day 3: Next.js UI + streaming (SSE)
- [x] Day 4: Admin dashboard (docs list, upload, stats) + query logging
- [x] Day 5: Dockerfile + Railway config + eval harness scaffold
- [x] Day 6: Hybrid search (BM25 + vector) with RRF fusion
- [x] Day 7: Local-first via Ollama (zero-cost default) + demo video

## Demo video

See [`DEMO.md`](./DEMO.md) for the 2-minute walkthrough.

## License

MIT
