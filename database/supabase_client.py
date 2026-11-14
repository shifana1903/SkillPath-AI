"""
Supabase PostgreSQL Client & Data Access Layer for SkillPath AI.

Design Principles:
- Uses ONLY the existing Supabase tables (e.g., 'learners').
- Uses the standard Supabase anonymous/publishable key (never the service-role key).
- Respects Row Level Security (RLS) and never attempts to disable it.
- Catches and handles database permission errors (e.g., RLS policy rejections, code 42501) safely.
- Never crashes the application and never stores fake data.
"""

import os
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()

_supabase_client = None


def get_supabase_client():
    """
    Initializes and returns the Supabase client singleton using public anon credentials.
    Returns None if credentials are missing or invalid.
    """
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if not SUPABASE_URL or not SUPABASE_KEY:
        return None

    try:
        from supabase import create_client
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return _supabase_client
    except Exception as e:
        print(f"[ERROR] Failed to initialize Supabase client: {e}")
        return None


class SupabaseService:
    """
    Data Access Layer interacting with existing Supabase tables.
    Gracefully manages RLS constraints and permission errors.
    """

    def __init__(self):
        self.client = get_supabase_client()

    @property
    def is_connected(self) -> bool:
        """Checks if client credentials are provided and client is initialized."""
        return self.client is not None

    def test_connection(self) -> Dict[str, Any]:
        """
        Tests the connection to Supabase and inspects the 'learners' table.
        """
        if not self.is_connected:
            return {
                "connected": False,
                "message": "Supabase credentials missing in .env",
                "details": "Please set SUPABASE_URL and SUPABASE_KEY."
            }

        try:
            # Query existing 'learners' table
            response = self.client.table("learners").select("*").limit(1).execute()
            return {
                "connected": True,
                "table_found": True,
                "message": "Connected to Supabase. 'learners' table accessible.",
                "sample_count": len(response.data) if response.data else 0
            }
        except Exception as e:
            error_str = str(e)
            if "42501" in error_str or "row-level security" in error_str.lower():
                return {
                    "connected": True,
                    "table_found": True,
                    "message": "Connected to Supabase ('learners' has RLS enabled).",
                    "details": error_str
                }
            return {
                "connected": False,
                "table_found": False,
                "message": f"Supabase query error: {error_str}",
                "details": error_str
            }

    def save_learner_profile(self, name: str, email: str, education: str) -> Dict[str, Any]:
        """
        Inserts or updates learner details in the existing 'learners' table.
        Safely catches RLS (42501) permission errors.
        """
        if not self.is_connected:
            return {
                "success": False,
                "permission_error": False,
                "message": "Supabase is not configured. Profile kept in current session."
            }

        payload = {
            "name": name.strip(),
            "email": email.strip(),
            "education": education.strip()
        }

        try:
            response = self.client.table("learners").insert(payload).execute()
            return {
                "success": True,
                "permission_error": False,
                "data": response.data,
                "message": "Learner profile saved successfully to Supabase!"
            }
        except Exception as e:
            error_msg = str(e)
            # Detect Row Level Security restriction (PGRST 42501)
            is_rls_error = "42501" in error_msg or "row-level security" in error_msg.lower()

            return {
                "success": False,
                "permission_error": is_rls_error,
                "error_details": error_msg,
                "message": (
                    "Supabase RLS is active: anon role lacks INSERT permission on 'learners'. "
                    "Profile is preserved in local session."
                    if is_rls_error
                    else f"Database error: {error_msg}"
                )
            }

    def fetch_all_learners(self) -> List[Dict[str, Any]]:
        """
        Fetches all learner records from the existing 'learners' table.
        """
        if not self.is_connected:
            return []

        try:
            response = self.client.table("learners").select("*").order("created_at", desc=True).execute()
            return response.data or []
        except Exception as e:
            print(f"[WARNING] Could not fetch learners: {e}")
            return []

    def record_progress(self, learner_email: str, completed_tasks: List[str]) -> Dict[str, Any]:
        """
        Attempts to persist completed task progress into Supabase.
        Safely captures permission issues when RLS prohibits unauthenticated writes.
        """
        if not self.is_connected:
            return {
                "success": False,
                "permission_error": False,
                "message": "Database not connected. Progress kept in active session."
            }

        # Try to record progress if a dedicated progress table exists or fallback cleanly
        try:
            # Check if there is an update hook or table
            response = self.client.table("learners").select("id").eq("email", learner_email).limit(1).execute()
            if response.data:
                learner_id = response.data[0]["id"]
                # Try saving to user_progress if table was created
                try:
                    self.client.table("user_progress").upsert({
                        "user_id": str(learner_id),
                        "completed_tasks": completed_tasks
                    }).execute()
                    return {"success": True, "message": "Progress persisted to Supabase."}
                except Exception:
                    pass

            return {
                "success": False,
                "permission_error": True,
                "message": "RLS policy or schema enforces read-only for anonymous client. Progress saved in session."
            }
        except Exception as e:
            return {
                "success": False,
                "permission_error": "42501" in str(e),
                "message": f"Database operation handled safely: {e}"
            }
