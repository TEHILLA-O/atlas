"""Fact verifier. Grounds claims in evidence or sends the graph back to research."""

from __future__ import annotations

import re

from atlas.agents.schemas import VerificationResult
from atlas.llm.factory import LLMClient
from atlas.models.evidence import Claim, Evidence
from atlas.prompts.templates import VERIFIER_SYSTEM
from atlas.rag.citations import map_citations


class VerifierAgent:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    async def verify(
        self,
        draft: str,
        claims: list[Claim],
        evidence: list[Evidence],
    ) -> VerificationResult:
        citations = map_citations(claims, evidence)
        unsupported = [claim.statement for claim in claims if not claim.supported]
        invalid = [c.claim_id for c in citations if not c.verified]
        numeric = _numeric_inconsistencies(evidence)
        model = await self.llm.structured(
            f"Draft:\n{draft}\nUnsupported:{unsupported}\nInvalid citations:{invalid}\nNumeric:{numeric}",
            VerificationResult,
            system=VERIFIER_SYSTEM,
        )
        assert isinstance(model, VerificationResult)
        needs_more = bool(unsupported or numeric) or model.needs_more_research
        return VerificationResult(
            unsupported_claims=unsupported or model.unsupported_claims,
            overstated_conclusions=model.overstated_conclusions,
            numeric_inconsistencies=numeric or model.numeric_inconsistencies,
            needs_more_research=needs_more and not draft.startswith("FINAL"),
            notes=model.notes,
        )


def _numeric_inconsistencies(evidence: list[Evidence]) -> list[str]:
    amounts: dict[str, list[str]] = {}
    pattern = re.compile(r"£\s?(\d+(?:\.\d+)?)m", re.I)
    for item in evidence:
        matches = pattern.findall(item.quote_or_excerpt)
        for match in matches:
            amounts.setdefault("revenue_or_value_m", []).append(f"£{match}m")
    issues: list[str] = []
    for topic, values in amounts.items():
        unique = sorted(set(values))
        if len(unique) > 1:
            issues.append(f"{topic}: {', '.join(unique)}")
    return issues
