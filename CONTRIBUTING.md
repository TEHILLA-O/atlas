# Contributing

Thanks for helping with Atlas. Prefer changes that keep evidence chains, tool allow-lists, and evaluation honest.

## Prerequisites

- Python 3.12 (see `.python-version`; requires `>=3.12,<3.14`)
- [uv](https://github.com/astral-sh/uv)
- Docker (optional) for Compose-based Postgres, Redis, API, and Streamlit
- Provider API keys only if you leave demo mode

## Setup

```bash
uv sync --extra dev
cp .env.example .env
```

Demo mode is the default (`MODEL_PROVIDER=demo`). Vendor keys are not required for tests or a local research pass.

## Run with Docker

```bash
docker compose up --build
```

Services: API `:8000`, Streamlit `:8501`, PostgreSQL 16 + pgvector, Redis.

## Run without full Compose

```bash
uv run atlas-api
# optional UI depending on apps layout
uv run streamlit run src/atlas/apps/ui/app.py
```

Ingest demo documents, then `POST /research` (interactive docs at `/docs`).

## Test and lint

```bash
uv run ruff check src tests apps
uv run pytest
uv run mypy src
```

Evaluation:

```bash
uv run atlas-eval
```

## Guidelines

- Do not invent citations. Mark unsupported claims instead.
- Keep tool access least privilege per agent.
- Avoid logging provider keys or raw secrets (see `docs/SECURITY.md`).
- Keep commit messages short and human.
