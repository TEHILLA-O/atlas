"""Deterministic contradiction detection, optionally enriched by an LLM."""

from __future__ import annotations

import re
from collections import defaultdict

from atlas.agents.schemas import ContradictionAnalysis
from atlas.llm.factory import LLMClient
from atlas.models.contradiction import Contradiction
from atlas.models.enums import ContradictionSeverity
from atlas.models.evidence import Evidence

_MONEY = re.compile(r"£\s?(\d+(?:\.\d+)?)\s*(m|million|bn|billion)?", re.I)
_YEAR = re.compile(r"\b(20\d{2})\b")


async def detect_contradictions(
    evidence: list[Evidence],
    llm: LLMClient | None = None,
) -> list[Contradiction]:
    found = _numeric_conflicts(evidence)
    if llm is not None:
        try:
            analysis = await llm.structured(
                "Identify contradictions among these excerpts:\n"
                + "\n".join(f"{item.evidence_id}: {item.quote_or_excerpt}" for item in evidence[:20]),
                ContradictionAnalysis,
            )
            assert isinstance(analysis, ContradictionAnalysis)
            found.extend(_from_llm(analysis, evidence))
        except Exception:
            pass
    return _dedupe(found)


def _numeric_conflicts(evidence: list[Evidence]) -> list[Contradiction]:
    buckets: dict[str, list[tuple[Evidence, str]]] = defaultdict(list)
    for item in evidence:
        for match in _MONEY.finditer(item.quote_or_excerpt):
            amount = match.group(1)
            unit = (match.group(2) or "m").lower()
            key = "annual revenue" if "revenue" in item.quote_or_excerpt.lower() or "turnover" in item.quote_or_excerpt.lower() else "monetary figure"
            label = f"£{amount}{unit[0] if unit else 'm'}"
            buckets[key].append((item, label))
        years = _YEAR.findall(item.quote_or_excerpt)
        if years:
            buckets["year mentioned"].append((item, years[0]))
    contradictions: list[Contradiction] = []
    for topic, pairs in buckets.items():
        unique_values = {label for _, label in pairs}
        if topic == "year mentioned":
            continue
        if len(unique_values) < 2:
            continue
        first, second = pairs[0], pairs[1]
        if first[1] == second[1] and len(pairs) > 2:
            second = next(pair for pair in pairs if pair[1] != first[1])
        contradictions.append(
            Contradiction(
                topic=topic,
                claim_a=first[1],
                claim_b=second[1],
                evidence_a_id=first[0].evidence_id,
                evidence_b_id=second[0].evidence_id,
                severity=ContradictionSeverity.HIGH if topic == "annual revenue" else ContradictionSeverity.MEDIUM,
                possible_explanation="Different reporting periods or definitions.",
                resolved=False,
            )
        )
    return contradictions


def _from_llm(analysis: ContradictionAnalysis, evidence: list[Evidence]) -> list[Contradiction]:
    ids = [item.evidence_id for item in evidence]
    results: list[Contradiction] = []
    for draft in analysis.items:
        a = draft.claim_a
        b = draft.claim_b
        ev_a = ids[0] if ids else "unknown"
        ev_b = ids[1] if len(ids) > 1 else ev_a
        results.append(
            Contradiction(
                topic=draft.topic,
                claim_a=a,
                claim_b=b,
                evidence_a_id=ev_a,
                evidence_b_id=ev_b,
                severity=draft.severity,
                possible_explanation=draft.possible_explanation,
                resolved=draft.resolved,
            )
        )
    return results


def _dedupe(items: list[Contradiction]) -> list[Contradiction]:
    seen: set[tuple[str, str, str]] = set()
    unique: list[Contradiction] = []
    for item in items:
        key = (item.topic.lower(), item.claim_a, item.claim_b)
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique
