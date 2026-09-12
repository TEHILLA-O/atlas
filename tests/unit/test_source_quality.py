from __future__ import annotations

from atlas.models.enums import SourceQuality
from atlas.rag.source_quality import classify_source, reliability_for


def test_government_outranks_community() -> None:
    gov = classify_source(url="https://www.ncsc.gov.uk/cyberessentials/overview")
    blog = classify_source(url="https://news.example.com/acme-revenue-thread")
    assert gov == SourceQuality.GOVERNMENT
    assert blog == SourceQuality.COMMUNITY
    assert reliability_for(gov) > reliability_for(blog)


def test_company_hint_and_media() -> None:
    assert classify_source(filename="briefing.pdf", source_hint="internal company") == SourceQuality.COMPANY_SOURCE
    assert classify_source(url="https://www.bbc.co.uk/news/technology") == SourceQuality.ESTABLISHED_MEDIA
