import json
from typing import Iterator

from anthropic import Anthropic

from app.config import settings


_client = Anthropic(api_key=settings.anthropic_api_key)


SYSTEM = """You answer strictly from the provided context.
If the context does not contain the answer, say "I don't know based on the provided documents."
Cite sources inline using [chunk_id] after any factual claim."""


def stream_answer(question: str, context: list[dict]) -> Iterator[bytes]:
    ctx_block = "\n\n".join(f"[{c['id']}]\n{c['content']}" for c in context)
    user = f"Context:\n{ctx_block}\n\nQuestion: {question}"

    with _client.messages.stream(
        model=settings.anthropic_model,
        max_tokens=1024,
        system=SYSTEM,
        messages=[{"role": "user", "content": user}],
    ) as stream:
        for text in stream.text_stream:
            yield f"data: {json.dumps({'delta': text})}\n\n".encode()
        yield f"data: {json.dumps({'done': True, 'sources': [c['id'] for c in context]})}\n\n".encode()
