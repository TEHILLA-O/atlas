# ADR 005 — Provider-independent LLMs

## Status

Accepted

## Context

Tying domain logic to one vendor SDK makes the system brittle and hard to demo.

## Decision

Agents depend on an `LLMClient` protocol. A factory selects OpenAI, Anthropic, Google, Ollama or the deterministic `demo` provider. Demo mode is first-class so the repository runs without keys.

## Consequences

- Tests never call paid APIs.
- Switching providers is a configuration change.
- Structured-output parsing is the client's responsibility.
