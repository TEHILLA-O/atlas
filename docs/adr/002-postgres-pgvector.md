# ADR 002 — PostgreSQL and pgvector

## Status

Accepted

## Context

Atlas must persist sessions, evidence, documents, reports and embeddings. A separate vector database would split transactional and retrieval data.

## Decision

Use PostgreSQL for all durable records and pgvector for embeddings. Hybrid retrieval combines cosine similarity with Postgres full-text search.

## Consequences

- One operational database.
- Transactions can cover document metadata and chunks.
- Embeddings require the `vector` extension, provided by `pgvector/pgvector` in Docker.
