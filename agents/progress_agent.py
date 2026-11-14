"""
Progress Tracking Agent for SkillPath AI.

Monitors real student milestone completions, calculates velocity and remaining workload,
and generates authentic AI feedback using Google Gemini based on completed tasks.
"""

from typing import List, Dict, Any, Set
from utils.helpers import call_gemini_model, format_progress_percentage


class ProgressAgent:
    """Agent responsible for progress calculations and personalized velocity feedback."""

    def __init__(self):
        pass

    def calculate_progress(
        self,
        all_tasks: List[Dict[str, Any]],
        completed_task_ids: Set[str]
    ) -> Dict[str, Any]:
        """
        Calculates exact progress metrics based on student checkbox actions.
        No fake data is generated.
        """
        total = len(all_tasks)
        completed_count = sum(1 for t in all_tasks if t.get("task_id") in completed_task_ids)
        percentage = format_progress_percentage(completed_count, total)

        total_hours = sum(t.get("estimated_hours", 4) for t in all_tasks)
        completed_hours = sum(
            t.get("estimated_hours", 4) for t in all_tasks if t.get("task_id") in completed_task_ids
        )
        remaining_hours = max(0, total_hours - completed_hours)

        return {
            "total_tasks": total,
            "completed_count": completed_count,
            "remaining_count": max(0, total - completed_count),
            "percentage": percentage,
            "total_hours": total_hours,
            "completed_hours": completed_hours,
            "remaining_hours": remaining_hours
        }

    def generate_progress_evaluation(
        self,
        student_name: str,
        target_career: str,
        all_tasks: List[Dict[str, Any]],
        completed_task_ids: Set[str]
    ) -> str:
        """
        Uses Gemini to generate real, dynamic feedback analyzing the specific tasks
        the student has marked complete vs what remains on their roadmap.
        """
        completed_titles = [
            t.get("title", "") for t in all_tasks if t.get("task_id") in completed_task_ids
        ]
        pending_titles = [
            t.get("title", "") for t in all_tasks if t.get("task_id") not in completed_task_ids
        ]

        total = len(all_tasks)
        completed = len(completed_titles)
        pct = format_progress_percentage(completed, total)

        if total == 0:
            return "No roadmap tasks generated yet. Head over to the Roadmap section to create your plan."

        if completed == 0:
            return (
                f"Welcome, {student_name}! You have {total} targeted milestones queued up for your "
                f"journey toward {target_career}. Check off your first completed task to initiate velocity tracking!"
            )

        prompt = f"""
You are an encouraging and disciplined engineering mentor.
Review this student's actual learning progress:

- Student: {student_name}
- Career Goal: {target_career}
- Progress: {completed}/{total} tasks complete ({pct}%)
- Completed Milestones: {', '.join(completed_titles)}
- Next Pending Tasks: {', '.join(pending_titles[:3])}

Write a 2-3 sentence personalized evaluation:
1. Acknowledge the specific technical concepts they just finished.
2. Provide a concrete tip for the very next pending milestone.
Keep it motivating, concise, and professional.
"""
        system_instruction = "You are a concise, motivating senior engineering leader."

        try:
            return call_gemini_model(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=0.4
            )
        except Exception as e:
            return f"Great progress! You have completed {completed} of {total} milestones ({pct}%). Keep building!"
