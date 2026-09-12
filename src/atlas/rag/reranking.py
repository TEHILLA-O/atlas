"""Lexical and optional model-based reranking."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from rank_bm25 import BM25Okapi


@dataclass(slots=True)
class RankedItem:
    text: str
    score: float
    payload: Any


def lexical_rerank(query: str, items: list[RankedItem], *, rerank_k: int) -> list[RankedItem]:
    if not items:
        return []
    corpus = [item.text.lower().split() for item in items]
    bm25 = BM25Okapi(corpus)
    scores = bm25.get_scores(query.lower().split())
    ranked = [
        RankedItem(text=item.text, score=float(score), payload=item.payload)
        for item, score in zip(items, scores, strict=True)
    ]
    ranked.sort(key=lambda item: item.score, reverse=True)
    return ranked[:rerank_k]


def merge_rrf(
    vector_hits: list[RankedItem],
    keyword_hits: list[RankedItem],
    *,
    k: int = 60,
) -> list[RankedItem]:
    """Reciprocal rank fusion of vector and keyword lists."""
    scores: dict[str, float] = {}
    payloads: dict[str, RankedItem] = {}
    for rank, item in enumerate(vector_hits, start=1):
        key = item.text
        scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
        payloads[key] = item
    for rank, item in enumerate(keyword_hits, start=1):
        key = item.text
        scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
        payloads[key] = item
    fused = [
        RankedItem(text=key, score=score, payload=payloads[key].payload)
        for key, score in scores.items()
    ]
    fused.sort(key=lambda item: item.score, reverse=True)
    return fused
