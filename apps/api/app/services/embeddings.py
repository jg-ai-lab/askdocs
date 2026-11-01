from openai import OpenAI

from app.config import settings


_client = OpenAI(api_key=settings.openai_api_key)


def embed_batch(texts: list[str]) -> list[list[float]]:
    resp = _client.embeddings.create(model=settings.embedding_model, input=texts)
    return [d.embedding for d in resp.data]


def embed_one(text: str) -> list[float]:
    return embed_batch([text])[0]
