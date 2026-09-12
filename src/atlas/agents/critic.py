"""Critic agent: attacks reasoning, does not rewrite the answer."""

from __future__ import annotations

from atlas.agents.schemas import CriticResult
from atlas.llm.factory import LLMClient
from atlas.models.contradiction import Contradiction
from atlas.models.evidence import Evidence
from atlas.prompts.templates import CRITIC_SYSTEM


class CriticAgent:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    async def critique(
        self,
        draft: str,
        evidence: list[Evidence],
        contradictions: list[Contradiction],
    ) -> CriticResult:
        weak = [
            item.evidence_id
            for item in evidence
            if item.reliability_score < 0.5
        ]
        result = await self.llm.structured(
            f"Draft:\n{draft}\nWeak evidence IDs: {weak}\n"
            f"Unresolved contradictions: {[c.topic for c in contradictions if not c.resolved]}",
            CriticResult,
            system=CRITIC_SYSTEM,
        )
        assert isinstance(result, CriticResult)
        return result
