import tiktoken

from app.config import settings


_enc = tiktoken.get_encoding("cl100k_base")


def chunk_text(text: str) -> list[str]:
    tokens = _enc.encode(text)
    size = settings.chunk_size
    overlap = settings.chunk_overlap
    step = max(1, size - overlap)

    out: list[str] = []
    for start in range(0, len(tokens), step):
        piece = tokens[start : start + size]
        if not piece:
            break
        out.append(_enc.decode(piece).strip())
        if start + size >= len(tokens):
            break
    return [c for c in out if c]
