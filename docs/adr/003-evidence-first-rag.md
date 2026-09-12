# ADR 003 — Evidence-first RAG

## Status

Accepted

## Context

Naive "chat with PDF" systems retrieve text and let the model invent citations. That is unacceptable for decision intelligence.

## Decision

Retrieval produces `Evidence` objects. Claims link to evidence IDs. Citations that cannot be mapped are marked unsupported. The verifier can send the graph back to research rather than fabricate a source.

## Consequences

- Reports may contain unknowns.
- Evaluation can score groundedness deterministically.
- Users can inspect the claim → evidence → source chain.
