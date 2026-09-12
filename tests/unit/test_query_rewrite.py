from __future__ import annotations

from atlas.rag.query_rewrite import rewrite_query
from atlas.rag.reranking import RankedItem, merge_rrf


def test_rewrite_and_rrf() -> None:
    variants = rewrite_query('Analyse the "Cyber Essentials Plus" requirement')
    assert variants
    assert any("Cyber Essentials Plus" in item for item in variants)
    fused = merge_rrf(
        [RankedItem(text="a", score=0.9, payload="a")],
        [RankedItem(text="b", score=0.8, payload="b"), RankedItem(text="a", score=0.7, payload="a")],
    )
    assert fused[0].text == "a"
