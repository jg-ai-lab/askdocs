"""Run the eval harness against the running API.

Usage:
    # 1. Start the API and ingest at least one doc
    # 2. Edit eval/questions.yaml with your titles
    # 3. python -m eval.run_eval http://localhost:8000

Reports top-K retrieval hit rate. Does NOT grade answer quality — that's
a separate layer best done with an LLM-as-judge or human review.
"""
import sys
from pathlib import Path

import httpx
import yaml

from app.services.embeddings import embed_one


def _load_questions() -> list[dict]:
    path = Path(__file__).parent / "questions.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))["questions"]


def _top_titles(api_url: str, question: str, k: int) -> list[str]:
    emb = embed_one(question)
    r = httpx.post(
        f"{api_url}/eval/retrieve",
        json={"embedding": emb, "k": k},
        timeout=30,
    )
    r.raise_for_status()
    return [row["title"] for row in r.json()]


def main(api_url: str = "http://localhost:8000", k: int = 5) -> None:
    questions = _load_questions()
    hits = 0
    for q in questions:
        titles = _top_titles(api_url, q["question"], k)
        hit = any(t in titles for t in q["expected_titles"])
        hits += int(hit)
        marker = "✓" if hit else "✗"
        print(f"{marker} {q['question']}")
        print(f"    expected: {q['expected_titles']}")
        print(f"    got:      {titles}")
    rate = hits / len(questions) if questions else 0
    print(f"\nTop-{k} hit rate: {hits}/{len(questions)} = {rate:.0%}")


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    main(url)
