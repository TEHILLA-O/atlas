from __future__ import annotations

from atlas.config.settings import Settings
from atlas.services.budget import BudgetTracker


def test_budget_blocks_unbounded_loops() -> None:
    settings = Settings(max_iterations=2, max_tokens=100, research_budget_usd=0.01, max_sources=3)
    tracker = BudgetTracker(settings)
    assert tracker.can_iterate()
    tracker.begin_iteration()
    tracker.begin_iteration()
    assert tracker.can_iterate() is False
    tracker.record(node="research", tokens=50, cost=0.02, sources=4)
    assert tracker.exceeded()
