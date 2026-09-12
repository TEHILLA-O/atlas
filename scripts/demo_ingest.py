"""Ingest bundled demo documents when PostgreSQL is available."""

from __future__ import annotations

import asyncio
from pathlib import Path

from atlas.cli.ingest import _ingest

DEMO_DIR = Path(__file__).resolve().parents[1] / "demo" / "documents"


def main() -> None:
    paths = sorted(DEMO_DIR.glob("*"))
    asyncio.run(_ingest(paths))


if __name__ == "__main__":
    main()
