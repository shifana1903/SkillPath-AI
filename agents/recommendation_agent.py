"""
Learning Recommendation Agent for SkillPath AI.

Generates a step-by-step, actionable personalized learning roadmap
with concrete tasks, curated resources, and milestone checkpoints using Google Gemini.
"""

from typing import List, Dict, Any, Union
from utils.helpers import call_gemini_model, clean_llm_json_response


class RecommendationAgent:
    """Agent responsible for crafting personalized, phased learning roadmaps."""

    def __init__(self):
        pass

    def generate_roadmap(
        self,
        student_name: str,
        target_career: str,
        missing_skills: Union[List[str], List[Dict[str, Any]]],
        hours_per_week: int = 10,
        learning_style: str = "Hands-on projects & documentation"
    ) -> Dict[str, Any]:
        """
        Creates a structured, task-by-task roadmap designed to close the identified skill gaps.
        Returns a dictionary containing phases and actionable tasks with unique IDs.
        """
        # Format missing skills
        skills_formatted = []
        for s in missing_skills:
            if isinstance(s, dict):
                skills_formatted.append(f"{s.get('skill', '')} ({s.get('importance', 'High')})")
            else:
                skills_formatted.append(str(s))

        missing_skills_str = ", ".join(skills_formatted) if skills_formatted else "Advanced Domain Projects"

        prompt = f"""
You are an elite technical curriculum architect.
Create a personalized, step-by-step learning roadmap for:

- Student Name: {student_name}
- Target Career: {target_career}
- High-Priority Missing Skills to Master: {missing_skills_str}
- Weekly Time Commitment: {hours_per_week} hours/week
- Learning Preference: {learning_style}

Break down the roadmap into 3 logical phases (Foundations, Applied Building, Capstone/Portfolio).
Include 5 to 8 specific, actionable tasks in total across the phases.
Each task MUST have a unique "task_id" (e.g. "task_1", "task_2", ...).

Return ONLY valid JSON matching this exact structure:
{{
  "roadmap_title": "<e.g., Personalized Path to {target_career}>",
  "total_estimated_weeks": <integer, e.g. 8>,
  "estimated_total_hours": <integer, e.g. 60>,
  "phases": [
    {{
      "phase_name": "<e.g. Phase 1: Core Fundamentals & Prerequisite Tools>",
      "goal": "<1-sentence milestone goal>",
      "tasks": [
        {{
          "task_id": "task_1",
          "title": "<Task Title>",
          "target_skill": "<Skill>",
          "description": "<Detailed learning action & hands-on mini-exercise>",
          "estimated_hours": <integer, e.g. 6>,
          "resources": [
            {{"title": "<Resource or Doc name>", "type": "<Docs/Tutorial/Project>", "url_hint": "<Source name or domain>"}}
          ]
        }}
      ]
    }}
  ]
}}
"""
        system_instruction = (
            "You are a structured technical curriculum planner. "
            "Every task must be concrete, highly practical, and feasible. "
            "Output pure JSON only."
        )

        response_text = call_gemini_model(
            prompt=prompt,
            system_instruction=system_instruction,
            json_mode=True,
            temperature=0.3
        )

        parsed_data = clean_llm_json_response(response_text)
        if isinstance(parsed_data, dict) and "phases" in parsed_data:
            return parsed_data

        raise ValueError(f"Failed to parse learning roadmap JSON: {response_text[:200]}")
