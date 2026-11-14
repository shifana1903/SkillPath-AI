"""
Helper utilities for SkillPath AI.

Includes:
- Streamlit CSS injection
- Google GenAI client initialization and resilient generation with google-genai
- JSON parser for agent outputs
- Formatting and calculation helpers
"""

import os
import re
import json
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

# Global cached client instance
_gemini_client = None

# Preferred Gemini model priority list (using google-genai SDK)
GEMINI_MODELS = ["gemini-3.1-flash-lite", "gemini-3.8-flash"]


def load_css(css_file_path: str = "assets/style.css") -> str:
    """Reads a CSS file and wraps it in <style> tags for Streamlit injection."""
    if os.path.exists(css_file_path):
        with open(css_file_path, "r", encoding="utf-8") as f:
            return f"<style>{f.read()}</style>"
    return ""


def get_gemini_client():
    """
    Initializes and caches the google-genai Client.
    Returns None if GEMINI_API_KEY is not configured.
    """
    global _gemini_client
    if _gemini_client is not None:
        return _gemini_client

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        return None

    try:
        from google import genai
        _gemini_client = genai.Client(api_key=api_key)
        return _gemini_client
    except Exception as e:
        print(f"[ERROR] Failed to initialize google-genai Client: {e}")
        return None


def call_gemini_model(
    prompt: str,
    system_instruction: Optional[str] = None,
    json_mode: bool = False,
    temperature: float = 0.4
) -> str:
    """
    Executes a prompt using google-genai with fallback model support and timeout handling.
    Raises RuntimeError if generation fails, ensuring no fake data is generated.
    """
    client = get_gemini_client()
    if not client:
        raise RuntimeError("Gemini API key is missing or invalid in your .env file.")

    from google.genai import types

    last_error = None
    for model_name in GEMINI_MODELS:
        try:
            config = types.GenerateContentConfig(
                temperature=temperature,
                http_options={"timeout": 25000}
            )
            if system_instruction:
                config.system_instruction = system_instruction
            if json_mode:
                config.response_mime_type = "application/json"

            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config
            )
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            last_error = e
            print(f"[WARNING] Model {model_name} failed: {e}. Trying fallback...")
            continue

    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")


def clean_llm_json_response(raw_text: str) -> Optional[Any]:
    """
    Extracts and parses JSON from LLM output, safely handling markdown code fences.
    """
    if not raw_text:
        return None

    cleaned = raw_text.strip()

    # Match JSON markdown block if present
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if match:
        cleaned = match.group(1).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback: attempt to find first '{' or '[' to last '}' or ']'
        try:
            start_curly = cleaned.find("{")
            start_bracket = cleaned.find("[")
            if start_curly != -1 and (start_bracket == -1 or start_curly < start_bracket):
                end_curly = cleaned.rfind("}")
                if end_curly != -1:
                    return json.loads(cleaned[start_curly:end_curly + 1])
            elif start_bracket != -1:
                end_bracket = cleaned.rfind("]")
                if end_bracket != -1:
                    return json.loads(cleaned[start_bracket:end_bracket + 1])
        except Exception:
            pass
        return None


def format_progress_percentage(completed: int, total: int) -> float:
    """Calculates completion percentage safely avoiding division by zero."""
    if total <= 0:
        return 0.0
    return round((completed / total) * 100, 1)
