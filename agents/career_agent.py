"""
Career Matching Agent for SkillPath AI.

Analyzes a student's existing skills, proficiency levels, and educational background
to recommend the most suitable tech career paths with match percentages and transition advice.
"""

from typing import List, Dict, Any
from utils.helpers import call_gemini_model, clean_llm_json_response


class CareerAgent:
    """Agent responsible for identifying optimal career paths based on a student's skills."""

    def __init__(self):
        pass

    def match_careers(
        self,
        education: str,
        skills_with_levels: List[Dict[str, str]],
        interests: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Suggests top career matches based on the student's skills and background using Gemini.
        Returns a list of career match objects.
        """
        skills_str = ", ".join(
            f"{s.get('skill', '')} ({s.get('level', 'Beginner')})"
            for s in skills_with_levels if s.get("skill")
        )
        if not skills_str:
            skills_str = "Foundational curiosity, beginner in computer concepts"

        prompt = f"""
You are an expert tech career advisor and talent intelligence consultant.
Analyze this learner profile:

- Educational Background: {education or 'General Technical'}
- Current Skills & Proficiency: {skills_str}
- Expressed Interests: {interests or 'Open to software and data domains'}

Identify the TOP 3 to 4 tech career roles that best leverage their current capabilities.
Return ONLY valid JSON matching this exact structure:
{{
  "recommendations": [
    {{
      "role_title": "<Role Name, e.g. Junior Backend Developer>",
      "match_percentage": <integer from 40 to 95>,
      "why_good_fit": "<1-2 sentences detailing how their current skills apply>",
      "key_strengths_utilized": ["<Skill 1>", "<Skill 2>"],
      "skills_to_bridge": ["<Skill to learn>", "<Skill to learn>"],
      "market_demand": "<Very High / High / Moderate>",
      "estimated_timeline": "<e.g. 8-12 weeks>"
    }}
  ]
}}
"""
        system_instruction = (
            "You are an insightful technical career advisor. "
            "Suggest realistic, in-demand roles with accurate match percentages. "
            "Output pure JSON only."
        )

        response_text = call_gemini_model(
            prompt=prompt,
            system_instruction=system_instruction,
            json_mode=True,
            temperature=0.3
        )

        parsed_data = clean_llm_json_response(response_text)
        if isinstance(parsed_data, dict) and "recommendations" in parsed_data:
            return parsed_data["recommendations"]
        elif isinstance(parsed_data, list):
            return parsed_data

        raise ValueError(f"Failed to parse career matches JSON: {response_text[:200]}")
