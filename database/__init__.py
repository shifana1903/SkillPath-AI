"""
Database Module for SkillPath AI.
"""

from .supabase_client import get_supabase_client, SupabaseService

__all__ = ["get_supabase_client", "SupabaseService"]
