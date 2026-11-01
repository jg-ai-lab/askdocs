"""LLM providers for grounded answers.

Default: Ollama (qwen2.5:7b) — fully local, zero API cost.
Opt-in: Anthropic Claude — higher quality on complex questions, paid.
"""
import json
from typing import Iterator

import httpx

from app.config import settings


SYSTEM = """You answer strictly from the provided context.
If the context does not contain the answer, say "I don't know based on the provided documents."
Cite sources inline using [chunk_id] after any factual claim."""


def stream_answer_tracked(question: str, context: list[dict]) -> Iterator[dict]:
    ctx_block = "\n\n".join(f"[{c['id']}]\n{c['content']}" for c in context)
    user = f"Context:\n{ctx_block}\n\nQuestion: {question}"
    if settings.llm_provider == "anthropic":
        yield from _stream_anthropic(user)
    else:
        yield from _stream_ollama(user)


def _stream_anthropic(user: str) -> Iterator[dict]:
    from anthropic import Anthropic

    client = Anthropic(api_key=settings.anthropic_api_key)
    with client.messages.stream(
        model=settings.anthropic_model,
        max_tokens=1024,
        system=SYSTEM,
        messages=[{"role": "user", "content": user}],
    ) as stream:
        for text in stream.text_stream:
            yield {"delta": text}
        final = stream.get_final_message()
        yield {
            "usage": {
                "input_tokens": final.usage.input_tokens,
                "output_tokens": final.usage.output_tokens,
            }
        }


def _stream_ollama(user: str) -> Iterator[dict]:
    url = settings.ollama_base_url + "/api/chat"
    payload = {
        "model": settings.ollama_llm_model,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
        "stream": True,
    }
    with httpx.Client(timeout=None) as client:
        with client.stream("POST", url, json=payload) as r:
            r.raise_for_status()
            input_tokens = 0
            output_tokens = 0
            for line in r.iter_lines():
                if not line:
                    continue
                data = json.loads(line)
                msg = data.get("message") or {}
                if msg.get("content"):
                    yield {"delta": msg["content"]}
                if data.get("done"):
                    input_tokens = data.get("prompt_eval_count", 0)
                    output_tokens = data.get("eval_count", 0)
            yield {"usage": {"input_tokens": input_tokens, "output_tokens": output_tokens}}
