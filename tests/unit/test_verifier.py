from __future__ import annotations

import pytest

from atlas.agents.verifier import VerifierAgent, _numeric_inconsistencies
from atlas.llm.providers.demo import DemoLLM
from atlas.models.enums import SourceType
from atlas.models.evidence import Claim, Evidence


def test_numeric_inconsistency_detection() -> None:
    evidence = [
        Evidence(claim="a", quote_or_excerpt="revenue was £15m", source_type=SourceType.DOCUMENT),
        Evidence(claim="b", quote_or_excerpt="revenue was £21m", source_type=SourceType.WEB),
    ]
    issues = _numeric_inconsistencies(evidence)
    assert issues


@pytest.mark.asyncio
async def test_verifier_flags_unsupported_claim() -> None:
    agent = VerifierAgent(DemoLLM())
    result = await agent.verify(
        "Draft recommendation",
        [Claim(statement="Secret CCS lot already awarded", evidence_ids=["missing"])],
        [],
    )
    assert result.unsupported_claims
