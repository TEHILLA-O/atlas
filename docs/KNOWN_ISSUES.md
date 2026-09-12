# Known issues

These are honest limitations, not hidden unfinished work.

## Live web search

The default `web_search` tool uses a curated public-style catalogue so the repository runs without search-API keys. Plug in a commercial search provider behind the same typed interface when deploying.

## Live page fetch

`fetch_web_page` enforces SSRF rules but does not perform unrestricted internet I/O in demo mode. This is deliberate.

## Embedding quality in demo mode

Demo embeddings are deterministic hash projections. They are good enough for tests and local demos; use OpenAI or Ollama embeddings in production.

## Checkpoint store

The API process uses an in-memory LangGraph checkpointer plus PostgreSQL for domain artefacts. Multi-replica production should swap in `langgraph-checkpoint-postgres`.

## PDF export

Reports are Markdown and JSON. PDF export is not implemented.

## LLM-as-judge

Evaluation prefers deterministic metrics. An optional LLM judge is not required to run the suite.

## Browser UI

The Streamlit UI is a thin client. It is not a full product frontend.
