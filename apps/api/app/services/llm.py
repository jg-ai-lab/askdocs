from typing import Iterator

from anthropic import Anthropic

from app.config import settings


_client = Anthropic(api_key=settings.anthropic_api_key)


SYSTEM = """You answer strictly from the provided context.
If the context does not contain the answer, say "I don't know based on the provided documents."
Cite sources inline using [chunk_id] after any factual claim."""


def stream_answer_tracked(question: str, context: list[dict]) -> Iterator[dict]:
    ctx_block = "\n\n".join(f"[{c['id']}]\n{c['content']}" for c in context)
    user = f"Context:\n{ctx_block}\n\nQuestion: {question}"

    with _client.messages.stream(
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
