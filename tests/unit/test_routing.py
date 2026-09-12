from __future__ import annotations

from atlas.graph.routing import after_analyse, after_human, after_verify, dispatch_research
from atlas.graph.state import ResearchState


def test_dispatch_creates_fanout() -> None:
    state: ResearchState = {
        "research_id": "r1",
        "user_query": "q",
        "research_plan": [{"id": "t1", "question": "q1"}, {"id": "t2", "question": "q2"}],
    }
    sends = dispatch_research(state)
    assert isinstance(sends, list)
    assert len(sends) == 2


def test_empty_plan_skips_to_analyse() -> None:
    assert dispatch_research({"research_id": "r", "user_query": "q", "research_plan": []}) == "analyse"


def test_iteration_and_human_routes() -> None:
    assert after_analyse({"needs_more_research": True}) == "plan"
    assert after_verify({"needs_more_research": False}) == "critic"
    assert after_human({"human_decision": "cancel"}) == "cancelled"
    assert after_human({"human_decision": "request_more_research", "iteration": 3}) == "finalise"
    assert after_human({"status": "awaiting_human"}) == "awaiting"
