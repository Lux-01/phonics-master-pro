"""
Omnibot Research Module
Coordinates multi-source research with sub-agents.
"""

from .research_orchestrator import ResearchOrchestrator, ResearchResult
from .design_researcher import DesignResearcher, DesignTrends

__all__ = [
    "ResearchOrchestrator",
    "ResearchResult", 
    "DesignResearcher",
    "DesignTrends"
]