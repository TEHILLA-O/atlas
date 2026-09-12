from __future__ import annotations

from atlas.models.enums import SourceType
from atlas.models.evidence import Claim, Evidence
from atlas.rag.citations import find_unsupported_claims, map_citations


def test_citations_map_only_real_evidence() -> None:
    evidence = Evidence(
        claim="Buyers require Cyber Essentials Plus",
        quote_or_excerpt="Public-sector buyers require Cyber Essentials Plus for relevant contracts.",
        source_type=SourceType.WEB,
        source_url="https://www.ncsc.gov.uk/cyberessentials/overview",
        relevance_score=0.9,
        reliability_score=0.95,
    )
    supported = Claim(statement="Buyers require Cyber Essentials Plus", evidence_ids=[evidence.evidence_id])
    invented = Claim(statement="Acme already holds a secret CCS lot", evidence_ids=["does-not-exist"])
    citations = map_citations([supported, invented], [evidence])
    assert supported.supported is True
    assert invented.supported is False
    assert all(item.evidence_id == evidence.evidence_id for item in citations)
    assert find_unsupported_claims([supported, invented]) == [invented]


def test_citation_verification_requires_overlap() -> None:
    evidence = Evidence(
        claim="unrelated",
        quote_or_excerpt="The weather in Glasgow was wet.",
        source_type=SourceType.WEB,
        source_url="https://example.com/weather",
    )
    claim = Claim(
        statement="Public bodies require Cyber Essentials Plus accreditation",
        evidence_ids=[evidence.evidence_id],
    )
    citations = map_citations([claim], [evidence])
    assert citations[0].verified is False
