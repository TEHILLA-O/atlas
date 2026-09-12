"""Web search tool. Demo mode returns curated public-style snippets."""

from __future__ import annotations

from pydantic import BaseModel, Field

from atlas.config.settings import Settings
from atlas.rag.source_quality import classify_source, reliability_for
from atlas.tools.base import ToolError, ToolResult


class WebSearchInput(BaseModel):
    query: str = Field(description="Search query for public web sources.")
    max_results: int = Field(default=5, ge=1, le=10)


class WebSearchTool:
    name = "web_search"
    description = "Search public web sources for market, policy and company information."
    input_model = WebSearchInput

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def run(self, payload: BaseModel) -> ToolResult:
        assert isinstance(payload, WebSearchInput)
        if not self.settings.web_search_enabled:
            return ToolResult(
                tool=self.name,
                ok=False,
                error=ToolError(tool=self.name, message="web search disabled", retryable=False),
            )
        results = _demo_results(payload.query)[: payload.max_results]
        return ToolResult(tool=self.name, data={"query": payload.query, "results": results})


def _demo_results(query: str) -> list[dict[str, object]]:
    catalogue = [
        {
            "title": "UK government cyber security procurement guidance",
            "url": "https://www.gov.uk/guidance/cyber-security-procurement",
            "snippet": (
                "Public-sector buyers commonly require Cyber Essentials Plus and "
                "increasingly expect suppliers to evidence incident-response capability."
            ),
        },
        {
            "title": "NCSC Cyber Essentials",
            "url": "https://www.ncsc.gov.uk/cyberessentials/overview",
            "snippet": (
                "Cyber Essentials Plus is the independently assessed certification "
                "often used as a tender gate in UK public contracts."
            ),
        },
        {
            "title": "Industry note: UK public-sector cyber market",
            "url": "https://www.gartner.com/en/documents/uk-public-cyber",
            "snippet": (
                "Framework agreements remain the dominant route to market; "
                "specialist subcontractors win more often than new prime bidders."
            ),
        },
        {
            "title": "Community discussion of Acme Technology revenue",
            "url": "https://news.example.com/acme-revenue-thread",
            "snippet": "Commenters claim Acme Technology annual revenue was £21m last year.",
        },
        {
            "title": "Companies House snapshot (illustrative)",
            "url": "https://find-and-update.company-information.service.gov.uk/company/ACME",
            "snippet": "Filed accounts in a prior period reported turnover of £15m.",
        },
    ]
    tokens = {token.lower() for token in query.split() if len(token) > 3}
    scored: list[dict[str, object]] = []
    for item in catalogue:
        hay = f"{item['title']} {item['snippet']}".lower()
        overlap = sum(1 for token in tokens if token in hay) if tokens else 1
        quality = classify_source(url=str(item["url"]))
        scored.append(
            {
                **item,
                "source_quality": quality.value,
                "reliability": reliability_for(quality),
                "overlap": overlap,
            }
        )
    scored.sort(
        key=lambda row: (int(str(row["overlap"])), float(str(row["reliability"]))),
        reverse=True,
    )
    return scored
