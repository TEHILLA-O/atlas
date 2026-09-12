"""Source-quality classification used by confidence scoring."""

from __future__ import annotations

from urllib.parse import urlparse

from atlas.models.enums import SourceQuality

_GOVERNMENT = (
    ".gov.uk",
    ".gov",
    "legislation.gov.uk",
    "ons.gov.uk",
    "ncsc.gov.uk",
    "gov.uk",
)
_ACADEMIC = (".ac.uk", ".edu", "arxiv.org", "ssrn.com")
_MEDIA = (
    "bbc.co.uk",
    "ft.com",
    "reuters.com",
    "theguardian.com",
    "economist.com",
    "wsj.com",
)
_INDUSTRY = ("gartner.com", "forrester.com", "idc.com", "isaca.org")
_COMPANY = ("investor.", "ir.", "sec.gov")


QUALITY_WEIGHTS: dict[SourceQuality, float] = {
    SourceQuality.PRIMARY: 1.0,
    SourceQuality.GOVERNMENT: 0.95,
    SourceQuality.ACADEMIC: 0.9,
    SourceQuality.COMPANY_SOURCE: 0.7,
    SourceQuality.ESTABLISHED_MEDIA: 0.75,
    SourceQuality.INDUSTRY: 0.65,
    SourceQuality.COMMUNITY: 0.35,
    SourceQuality.UNKNOWN: 0.4,
}


def classify_source(
    *,
    url: str | None = None,
    filename: str | None = None,
    source_hint: str | None = None,
) -> SourceQuality:
    if source_hint:
        hint = source_hint.lower()
        if hint in {q.value.lower() for q in SourceQuality}:
            return SourceQuality(source_hint.upper())
        if "government" in hint or "official" in hint:
            return SourceQuality.GOVERNMENT
        if "internal" in hint or "company" in hint:
            return SourceQuality.COMPANY_SOURCE
    haystack = " ".join(part for part in [url or "", filename or ""] if part).lower()
    hostname = urlparse(url).hostname if url else None
    host = hostname.lower() if hostname else ""
    if any(token in haystack or token in host for token in _GOVERNMENT):
        return SourceQuality.GOVERNMENT
    if any(token in haystack or token in host for token in _ACADEMIC):
        return SourceQuality.ACADEMIC
    if any(token in haystack or token in host for token in _COMPANY):
        return SourceQuality.COMPANY_SOURCE
    if any(token in haystack or token in host for token in _MEDIA):
        return SourceQuality.ESTABLISHED_MEDIA
    if any(token in haystack or token in host for token in _INDUSTRY):
        return SourceQuality.INDUSTRY
    if filename and filename.lower().endswith((".pdf", ".docx")):
        return SourceQuality.COMPANY_SOURCE
    if url:
        return SourceQuality.COMMUNITY
    return SourceQuality.UNKNOWN


def reliability_for(quality: SourceQuality) -> float:
    return QUALITY_WEIGHTS[quality]
