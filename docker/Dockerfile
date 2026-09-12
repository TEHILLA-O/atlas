FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.6.3 /uv /usr/local/bin/uv

COPY pyproject.toml README.md ./
COPY src ./src
COPY apps ./apps
COPY alembic ./alembic
COPY alembic.ini ./
COPY demo ./demo

RUN uv pip install --system .

EXPOSE 8000
CMD ["uvicorn", "atlas.apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
