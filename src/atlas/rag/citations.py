"""Claim-to-evidence citation mapping. Unsupported claims stay unsupported."""

from __future__ import annotations

from atlas.models.evidence import Citation, Claim, Evidence


def map_citations(claims: list[Claim], evidence: list[Evidence]) -> list[Citation]:
    by_id = {item.evidence_id: item for item in evidence}
    citations: list[Citation] = []
    for claim in claims:
        linked = [by_id[eid] for eid in claim.evidence_ids if eid in by_id]
        claim.supported = bool(linked)
        claim.strength = _strength(linked) if linked else 0.0
        for item in linked:
            citations.append(
                Citation(
                    claim_id=claim.claim_id,
                    evidence_id=item.evidence_id,
                    source_ref=item.source_url or item.document_id or "unknown",
                    excerpt=item.quote_or_excerpt,
                    verified=_excerpt_supports(claim.statement, item.quote_or_excerpt),
                )
            )
    return citations


def find_unsupported_claims(claims: list[Claim]) -> list[Claim]:
    return [claim for claim in claims if not claim.supported]


def _strength(evidence: list[Evidence]) -> float:
    if not evidence:
        return 0.0
    return min(1.0, sum(item.reliability_score * item.relevance_score for item in evidence) / len(evidence))


def _excerpt_supports(statement: str, excerpt: str) -> bool:
    tokens = {token.lower() for token in statement.split() if len(token) > 3}
    if not tokens:
        return False
    excerpt_l = excerpt.lower()
    overlap = sum(1 for token in tokens if token in excerpt_l)
    return overlap / len(tokens) >= 0.25
