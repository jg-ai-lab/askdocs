"""Embedding providers.

Default: Ollama (nomic-embed-text) — fully local, zero API cost.
Opt-in: OpenAI text-embedding-3-small — higher quality on English, paid.

Switch via settings.embedding_provider.
"""
import httpx

from app.config import settings


def embed_batch(texts: list[str]) -> list[list[float]]:
    if settings.embedding_provider == "openai":
        return _openai_batch(texts)
    return _ollama_batch(texts)


def embed_one(text: str) -> list[float]:
    return embed_batch([text])[0]


def _ollama_batch(texts: list[str]) -> list[list[float]]:
    out: list[list[float]] = []
    with httpx.Client(timeout=120, base_url=settings.ollama_base_url) as client:
        for text in texts:
            r = client.post(
                "/api/embed",
                json={"model": settings.ollama_embedding_model, "input": text},
            )
            r.raise_for_status()
            data = r.json()
            # /api/embed returns {"embeddings": [[...]]}
            out.append(data["embeddings"][0])
    return out


def _openai_batch(texts: list[str]) -> list[list[float]]:
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    resp = client.embeddings.create(model=settings.openai_embedding_model, input=texts)
    return [d.embedding for d in resp.data]
