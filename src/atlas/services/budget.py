"""Hard cost and iteration limits. Prevents unbounded research loops."""

from __future__ import annotations

from dataclasses import dataclass, field

from atlas.config.settings import Settings


@dataclass
class BudgetTracker:
    settings: Settings
    tokens_used: int = 0
    cost_usd: float = 0.0
    iterations: int = 0
    sources: int = 0
    model_calls: int = 0
    events: list[dict[str, float | int | str]] = field(default_factory=list)

    def record(
        self,
        *,
        node: str,
        tokens: int = 0,
        cost: float = 0.0,
        sources: int = 0,
    ) -> None:
        self.tokens_used += tokens
        self.cost_usd += cost
        self.sources += sources
        self.model_calls += 1
        self.events.append(
            {"node": node, "tokens": tokens, "cost": cost, "sources": sources}
        )

    def can_iterate(self) -> bool:
        return self.iterations < self.settings.max_iterations

    def begin_iteration(self) -> None:
        self.iterations += 1

    def exceeded(self) -> bool:
        return (
            self.tokens_used >= self.settings.max_tokens
            or self.cost_usd >= self.settings.research_budget_usd
            or self.sources >= self.settings.max_sources
        )

    def snapshot(self) -> dict[str, float | int]:
        return {
            "tokens_used": self.tokens_used,
            "cost_usd": round(self.cost_usd, 4),
            "iterations": self.iterations,
            "sources": self.sources,
            "model_calls": self.model_calls,
        }
