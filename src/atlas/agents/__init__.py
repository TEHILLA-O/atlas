"""Specialised agents. Each has a distinct responsibility and tool set."""

from atlas.agents.critic import CriticAgent
from atlas.agents.document_analyst import DocumentAnalystAgent
from atlas.agents.planner import PlannerAgent
from atlas.agents.researcher import ResearcherAgent
from atlas.agents.synthesizer import SynthesizerAgent
from atlas.agents.verifier import VerifierAgent

__all__ = [
    "CriticAgent",
    "DocumentAnalystAgent",
    "PlannerAgent",
    "ResearcherAgent",
    "SynthesizerAgent",
    "VerifierAgent",
]
