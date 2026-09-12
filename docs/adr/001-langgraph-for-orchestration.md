# ADR 001 — LangGraph for research orchestration

## Status

Accepted

## Context

Atlas must run a multi-stage research workflow with branching, fan-out, retries and human approval. A single sequential script or a chat loop cannot represent those transitions.

## Decision

Use LangGraph `StateGraph` with a typed `ResearchState`. Each node has one responsibility. Conditional edges encode retry, verification failure and human review. Parallel research uses `Send` fan-out.

## Consequences

- Graph state is structured and checkpointable.
- Nodes are independently testable.
- Vendor chat APIs stay behind the LLM interface; the graph does not depend on one provider.
