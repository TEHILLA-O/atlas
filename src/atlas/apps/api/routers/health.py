"""Liveness and readiness probes."""

from __future__ import annotations

from fastapi import APIRouter, Request
from sqlalchemy import text

from atlas.persistence.session import get_engine

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def ready(request: Request) -> dict[str, str]:
    checks = {"api": "ok"}
    try:
        engine = get_engine(request.app.state.settings)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["postgres"] = "ok"
    except Exception:
        checks["postgres"] = "error"
    try:
        import redis.asyncio as redis

        client = redis.from_url(request.app.state.settings.redis_url)
        await client.ping()
        await client.close()
        checks["redis"] = "ok"
    except Exception:
        checks["redis"] = "error"
    status = "ok" if all(value == "ok" for value in checks.values()) else "degraded"
    return {"status": status, **checks}
