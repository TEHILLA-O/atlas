# Failure modes, fixes, and results

Honest engineering notes for this project. Nothing here is invented for polish.

## What can go wrong

- **Fabricated citations / unsupported claims.** Impact: bad decisions. Mitigation: evidence objects, citation verification, leave claims unsupported rather than invent sources.
- **Prompt injection, SSRF, oversized uploads.** Impact: tool abuse or internal fetch. Mitigation: tool allow-lists, SSRF URL rules, upload limits, HTML sanitisation, secret redaction (`docs/SECURITY.md`).
- **Demo-mode quality mistaken for production RAG.** Impact: misleading eval. Mitigation: curated catalogue search, restricted fetch, hash-projection embeddings called out in `docs/KNOWN_ISSUES.md`.
- **Multi-replica checkpoint loss.** Impact: lost graph state. Mitigation: in-memory LangGraph checkpointer for single process; swap to Postgres checkpointer for multi-replica (documented).

## What went wrong

**No recorded production incident in this repo yet.** Honest limitations tracked in `docs/KNOWN_ISSUES.md`:

1. Default `web_search` uses a curated catalogue (no live search API keys required).
2. `fetch_web_page` does not do unrestricted internet I/O in demo mode.
3. PDF export not implemented; Streamlit UI is a thin client.

## How it was resolved

- Known issues are documented rather than hidden; production providers plug into the same typed interfaces.
- Build progress phases 1-15+ mark evidence, contradiction detection, verifier/critic, and human-in-the-loop as implemented in code (`docs/BUILD_PROGRESS.md`).

## Results

- Evaluation prefers deterministic metrics; optional LLM-as-judge is not required to run the suite.
- Successful local demo: Docker Compose / uv, run a research question in demo mode, inspect cited report and human-review pause. No fabricated MRR or latency numbers here.
