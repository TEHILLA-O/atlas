"""Query rewriting for retrieval. Falls back to heuristic expansion."""

from __future__ import annotations

import re


def rewrite_query(query: str) -> list[str]:
    """Produce a small set of retrieval queries without requiring an LLM."""
    cleaned = " ".join(query.split())
    variants = [cleaned]
    without_stop = _drop_stops(cleaned)
    if without_stop and without_stop != cleaned:
        variants.append(without_stop)
    quoted = re.findall(r'"([^"]+)"', query)
    variants.extend(quoted)
    unique: list[str] = []
    for item in variants:
        if item and item not in unique:
            unique.append(item)
    return unique[:4]


_STOPS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "of",
    "to",
    "for",
    "in",
    "on",
    "should",
    "whether",
    "analyse",
    "analyze",
    "identify",
}


def _drop_stops(text: str) -> str:
    return " ".join(token for token in text.split() if token.lower() not in _STOPS)
