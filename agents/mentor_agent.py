"""
Mentor Agent for SkillPath AI.

Provides an interactive, context-aware AI engineering tutor and career mentor
powered by Google Gemini. Explains technical concepts, reviews code snippets,
and answers student questions tailored to their personalized learning roadmap.
"""

from typing import List, Dict, Any, Optional
from utils.helpers import call_gemini_model


class MentorAgent:
    """Agent responsible for interactive technical tutoring and conceptual guidance."""

    def __init__(self):
        pass

    def answer_question(
        self,
        question: str,
        student_context: Optional[Dict[str, Any]] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generates an authentic, step-by-step answer to a student's technical or career question.
        Incorporates student context (target career, current skills) for tailored relevance.
        """
        student_context = student_context or {}
        chat_history = chat_history or []

        student_name = student_context.get("name", "Student")
        target_career = student_context.get("target_career", "Software Engineering")
        education = student_context.get("education", "Undergraduate")

        skills = student_context.get("skills", [])
        skills_str = ", ".join(
            f"{s.get('skill', '')} ({s.get('level', '')})" for s in skills if s.get("skill")
        ) or "Beginner"

        # Format recent history (up to last 4 messages for context without overflow)
        history_context = ""
        if chat_history:
            formatted_turns = []
            for msg in chat_history[-4:]:
                role = "Student" if msg.get("role") == "user" else "Mentor"
                formatted_turns.append(f"{role}: {msg.get('content', '')}")
            history_context = "\nRecent Conversation:\n" + "\n".join(formatted_turns) + "\n"

        prompt = f"""
Student Background:
- Name: {student_name}
- Education: {education}
- Target Career: {target_career}
- Current Skill Profile: {skills_str}
{history_context}
Current Question from {student_name}:
"{question}"

Please provide a clear, insightful, and pedagogical explanation:
- Break complex concepts into easy-to-understand steps.
- Use a relatable real-world analogy if explaining an abstract computing concept.
- Include concise, well-commented code snippets if applicable.
- Conclude with a quick self-check question or actionable takeaway.
"""
        system_instruction = (
            f"You are the SkillPath AI Senior Tech Mentor assisting {student_name}. "
            f"Their goal is to become a top-tier {target_career}. "
            "Be patient, crystal-clear, pedagogically sound, and encouraging. Never make up facts."
        )

        return call_gemini_model(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.5
        )
