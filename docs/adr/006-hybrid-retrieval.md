# ADR 006 — Hybrid retrieval

## Status

Accepted

## Context

Vector similarity alone misses exact identifiers, money figures and policy names.

## Decision

Rewrite the query, run vector and keyword retrieval, fuse with reciprocal rank fusion, rerank lexically, then deduplicate. Thresholds (`top_k`, `rerank_k`, `min_similarity`) are configurable.

## Consequences

- Retrieval quality is tunable without changing agents.
- Keyword search depends on Postgres `tsvector`.
- Reranking can later swap in a cross-encoder without changing callers.
