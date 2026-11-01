# Failure modes, fixes, and results

Honest engineering notes for this project. Nothing here is invented for polish.

## What can go wrong

- **Fabricated citations / unsupported claims.** Impact: bad decisions. Mitigation: evidence objects, citation verification, leave claims unsupported rather than invent sources.
- **Prompt injection, SSRF, oversized uploads.** Impact: tool abuse or internal fetch. Mitigation: tool allow-lists, SSRF URL rules, upload limits, HTML sanitisation, secret redaction (`docs/SECURITY.md`).
- **Demo-mode quality mistaken for production RAG.** Impact: misleading eval. Mitigation: curated catalogue search, restricted fetch, hash-projection embeddings called out in `docs/KNOWN_ISSUES.md`.
- **Multi-replica checkpoint loss.** Impact: lost graph state. Mitigation: in-memory LangGraph checkpointer for single process; swap to Postgres checkpointer for multi-replica (documented).

## What went wrong

1. **`POST /research` returned 500 against Postgres (found 1 November 2026).** The orchestrator generated a `research_id` but `create_session` let the database row pick its own id, so saving contradictions failed with a foreign key error. Unit and graph tests did not touch the Postgres repositories, so it went unnoticed.
2. **Resuming a paused run returned 500.** `resume` saved the full state again, including evidence already stored, and hit a duplicate primary key.

Honest limitations tracked in `docs/KNOWN_ISSUES.md`:

1. Default `web_search` uses a curated catalogue (no live search API keys required).
2. `fetch_web_page` does not do unrestricted internet I/O in demo mode.
3. PDF export not implemented; Streamlit UI is a thin client.

## How it was resolved

- The session row now uses the run's `research_id`, and evidence and contradictions are merged by id instead of inserted, so start, pause, resume and report work end to end.

- Known issues are documented rather than hidden; production providers plug into the same typed interfaces.
- Build progress phases 1-15+ mark evidence, contradiction detection, verifier/critic, and human-in-the-loop as implemented in code (`docs/BUILD_PROGRESS.md`).

## Results

- Evaluation prefers deterministic metrics; optional LLM-as-judge is not required to run the suite.
- 1 November 2026, demo mode with uv, Postgres and Redis from Compose: a research run paused for review at confidence 0.64 with 2 contradictions, then completed with a cited report after approval. 30 tests pass, ruff and mypy are clean, `atlas-eval` mean 0.93 on 3 demo cases. The full Compose stack was not run. No MRR or latency numbers have been measured.
