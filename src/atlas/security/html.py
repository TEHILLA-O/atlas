"""HTML sanitisation for ingested pages."""

from __future__ import annotations

from bleach import clean

ALLOWED_TAGS = [
    "p",
    "br",
    "ul",
    "ol",
    "li",
    "h1",
    "h2",
    "h3",
    "h4",
    "strong",
    "em",
    "a",
    "blockquote",
    "code",
    "pre",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
]


def sanitise_html(html: str) -> str:
    return clean(
        html,
        tags=ALLOWED_TAGS,
        attributes={"a": ["href", "title"]},
        strip=True,
    )
