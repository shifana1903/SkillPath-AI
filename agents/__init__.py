"""
SkillPath AI Agent Modules.

This package contains modular AI agents powered by Gemini:
- SkillGapAgent: Analyzes differences between current skills and target role requirements.
- CareerAgent: Maps career trajectories, industry trends, and milestone roadmaps.
- RecommendationAgent: Curates personalized learning resources (courses, projects, docs).
- ProgressAgent: Monitors milestone completion and updates roadmap pacing.
- MentorAgent: Context-aware interactive tutor for Q&A, code review, and conceptual doubts.
"""

from .skill_gap_agent import SkillGapAgent
from .career_agent import CareerAgent
from .recommendation_agent import RecommendationAgent
from .progress_agent import ProgressAgent
from .mentor_agent import MentorAgent

__all__ = [
    "SkillGapAgent",
    "CareerAgent",
    "RecommendationAgent",
    "ProgressAgent",
    "MentorAgent"
]
