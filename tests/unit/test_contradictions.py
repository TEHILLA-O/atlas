from __future__ import annotations

import pytest

from atlas.models.enums import SourceType
from atlas.models.evidence import Evidence
from atlas.services.contradictions import detect_contradictions


@pytest.mark.asyncio
async def test_detects_revenue_conflict() -> None:
    evidence = [
        Evidence(
            claim="rev",
            quote_or_excerpt="Internal briefing states Acme Technology annual revenue was £15m.",
            source_type=SourceType.DOCUMENT,
            document_id="memo",
        ),
        Evidence(
            claim="rev",
            quote_or_excerpt="Commenters claim Acme Technology annual revenue was £21m last year.",
            source_type=SourceType.WEB,
            source_url="https://news.example.com/acme",
        ),
    ]
    found = await detect_contradictions(evidence)
    assert found
    assert any("15" in item.claim_a or "15" in item.claim_b for item in found)
    assert all(item.resolved is False for item in found)
