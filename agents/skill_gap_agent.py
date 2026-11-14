"""
Skill Gap Analysis Agent for SkillPath AI.

Uses Google Gemini to compare a student's current skills and proficiency levels
against real industry requirements for their target career role.
"""

from typing import List, Dict, Any
from utils.helpers import call_gemini_model, clean_llm_json_response


class SkillGapAgent:
    """Agent responsible for in-depth technical skill gap evaluation."""

    def __init__(self):
        pass

    def analyze_gap(
        self,
        student_name: str,
        education: str,
        target_career: str,
        skills_with_levels: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Compares existing skills against target career expectations using Gemini.
        Returns a structured dictionary with readiness score and missing competencies.
        """
        # Format the student's existing skills for the prompt
        skills_str = ", ".join(
            f"{s.get('skill', '')} ({s.get('level', 'Beginner')})"
            for s in skills_with_levels if s.get("skill")
        )
        if not skills_str:
            skills_str = "None specified yet (complete beginner)"

        prompt = f"""
You are an expert technical career architect and recruiter.
Analyze the following student profile for their desired target career:

- Student Name: {student_name}
- Education Background: {education}
- Target Career Role: {target_career}
- Current Skills & Proficiency Levels: {skills_str}

Evaluate the student's readiness and identify gaps based on current 2026 industry standards.
Return ONLY valid JSON matching this exact structure:
{{
  "readiness_score": <integer from 0 to 100>,
  "target_career_overview": "<concise 1-2 sentence summary of this role in industry>",
  "matched_skills": [
    {{"skill": "<skill name>", "current_level": "<level>", "feedback": "<short note>"}}
  ],
  "missing_skills": [
    {{"skill": "<skill name>", "category": "<Core/Tool/Architecture/Soft Skill>", "importance": "<Critical/High/Medium>", "reason": "<why needed>"}}
  ],
  "skill_level_upgrades": [
    {{"skill": "<skill>", "needed_level": "<Intermediate or Advanced>", "gap": "<what needs improvement>"}}
  ],
  "priority_focus_areas": [
    "<Focus 1>", "<Focus 2>", "<Focus 3>"
  ],
  "executive_summary": "<encouraging 2-3 sentence strategic summary for the student>"
}}
"""
        system_instruction = (
            "You are a rigorous yet supportive technical career evaluator. "
            "Deliver realistic, high-standard evaluations without generic filler. "
            "Output pure JSON only."
        )

        response_text = call_gemini_model(
            prompt=prompt,
            system_instruction=system_instruction,
            json_mode=True,
            temperature=0.3
        )

        parsed_data = clean_llm_json_response(response_text)
        if not isinstance(parsed_data, dict):
            raise ValueError(f"Failed to parse skill gap analysis JSON: {response_text[:200]}")

        # Ensure required keys exist with safe defaults
        parsed_data.setdefault("readiness_score", 45)
        parsed_data.setdefault("target_career_overview", f"Standard requirements for {target_career}")
        parsed_data.setdefault("matched_skills", [])
        parsed_data.setdefault("missing_skills", [])
        parsed_data.setdefault("skill_level_upgrades", [])
        parsed_data.setdefault("priority_focus_areas", [])
        parsed_data.setdefault("executive_summary", "Evaluation complete.")

        return parsed_data
