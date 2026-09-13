# Architecture

Atlas is an agentic research and decision-intelligence platform. It turns a complex question into a plan, gathers evidence from public and private sources, scores source quality, detects contradictions, verifies citations, estimates confidence, and can pause for human approval before a recommendation is final.

Atlas is not a chatbot wrapper and not a "chat with PDF" demo. Conversation history is not the system of record.

## Product purpose

Typical use: analyse whether a company should pursue a specific public-sector opportunity. Atlas classifies the request, generates structured subtasks, researches in parallel, retrieves uploaded documents, extracts evidence, then writes a cited report. Claims that cannot be grounded are marked unsupported instead of inventing URLs.

## Main components

| Component | Location / role |
| --- | --- |
| FastAPI API | Research runs, documents, feedback, memory, health (`apps` / `src/atlas`) |
| Streamlit UI | Optional operator view for plan, sources, evidence, contradictions, confidence |
| Research orchestrator | Compiles the LangGraph app and manages checkpoints |
| Agents | Classifier, planner, researchers, document analyst, contradiction detector, synthesiser, verifier, critic, human review |
| Tools | Least-privilege web and document tools (search, fetch, calculator, chunk retrieval) |
| RAG pipeline | Parse, chunk, embed, hybrid retrieve (vector + keyword), RRF, rerank, dedup |
| Stores | PostgreSQL + pgvector (domain data, vectors), Redis (supporting runtime needs) |
| Evaluation CLI | `atlas-eval` deterministic groundedness and citation checks |

## Layers

```text
API / Streamlit UI
        |
        v
Orchestrator (LangGraph compile + checkpoints)
        |
        v
Agents (planner, researcher, document analyst, verifier, critic, synthesiser)
        |
        v
Tools (least privilege) + RAG (hybrid retrieval)
        |
        v
PostgreSQL / pgvector / Redis
```

## Control flow

1. Classifier: intent, sensitivity, impact.
2. Planner: structured `ResearchTask`s and queries.
3. Parallel research: web tools, private document tools, RAG retrieval (LangGraph `Send` fan-out).
4. Evidence aggregator: structured evidence objects, not free-form footnotes.
5. Contradiction detector and gap analysis.
6. Synthesiser: grounded report draft.
7. Verifier: citation and numeric checks; may loop back to planning when evidence is insufficient.
8. Critic: attacks reasoning without silently rewriting claims.
9. Human review when confidence is low, impact is high, or material contradictions remain.
10. Final report (or cancel / more research via `POST /research/{id}/resume`).

The compiled graph lives in `src/atlas/graph/workflow.py`. State is a typed `ResearchState` (plan, evidence, contradictions, confidence, iteration, human decision).

## Evidence and citations

```text
Claim -> Citation -> Evidence -> Source (URL or document_id)
```

If the chain cannot be closed, the claim is `unsupported`. Sources are classified (PRIMARY, GOVERNMENT, ACADEMIC, COMPANY_SOURCE, ESTABLISHED_MEDIA, INDUSTRY, COMMUNITY, UNKNOWN) so weak blogs do not outrank stronger publications when both exist.

## RAG data flow

```text
Document -> parser -> metadata -> chunker -> embedding -> pgvector
Query -> rewrite -> vector search + keyword search -> RRF -> rerank -> dedup -> Evidence
```

Supported ingest formats include PDF, TXT, Markdown, DOCX, and HTML.

## Memory and checkpoints

Conversation/checkpoint state stays with the graph saver. Domain data remains in Postgres. Long-term memory is explicit (`POST /memory`) and removable. Swap the in-memory saver for `langgraph-checkpoint-postgres` when running multi-replica deploys.

## Repository layout

```
src/atlas/        library code (graph, agents, RAG, tools, domain)
apps/             API / UI entry layouts when split from the package
demo/             sample documents and scenarios
alembic/          schema migrations
docker/           container assets
scripts/          operator helpers
tests/            unit, graph, and evaluation tests
docs/             architecture, API, security, ADRs, known issues
```

## Related docs

- [API.md](API.md)
- [SECURITY.md](SECURITY.md)
- [KNOWN_ISSUES.md](KNOWN_ISSUES.md)
- ADRs under `docs/adr/`
