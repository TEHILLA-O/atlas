# ADR 004 — Human-in-the-loop

## Status

Accepted

## Context

High-impact recommendations and low-confidence conclusions should not be auto-finalised.

## Decision

Pause the graph before finalisation when confidence is below threshold, contradictions remain, or the request is high-impact. LangGraph interrupts plus `/research/{id}/resume` make the session resumable.

## Consequences

- Checkpointers are mandatory in production.
- The API exposes approve / request more research / cancel.
- Test environments auto-approve so CI can run the full graph.
