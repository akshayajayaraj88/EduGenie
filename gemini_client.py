"""Shared Google Gemini client used by every cloud-backed module."""

import json
import os
import re

from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "gemini-3.8-flash"


class GeminiError(Exception):
    """Raised when Gemini is not configured or returns an unusable response."""


_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise GeminiError(
                "GEMINI_API_KEY is not set. Copy .env.example to .env and add your key."
            )
        from google import genai

        _client = genai.Client(api_key=api_key)
    return _client


def model_name() -> str:
    return os.getenv("GEMINI_MODEL", DEFAULT_MODEL)


def generate(prompt: str, system: str | None = None, json_output: bool = False) -> str:
    """Send a prompt to Gemini and return the response text."""
    from google.genai import types

    config = types.GenerateContentConfig(
        system_instruction=system,
        temperature=0.4,
        response_mime_type="application/json" if json_output else None,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )
    try:
        response = _get_client().models.generate_content(
            model=model_name(), contents=prompt, config=config
        )
    except GeminiError:
        raise
    except Exception as exc:  # network errors, quota, invalid key, etc.
        raise GeminiError(f"Gemini request failed: {exc}") from exc

    text = (getattr(response, "text", None) or "").strip()
    if not text:
        raise GeminiError("Gemini returned an empty response. Please try again.")
    return text


def clean_json_block(text: str) -> str:
    """Strip Markdown code fences (```json ... ```) around a JSON payload."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text


def generate_json(prompt: str, system: str | None = None, retries: int = 1):
    """Ask Gemini for JSON and parse it, retrying once on invalid output."""
    last_error = None
    for _ in range(retries + 1):
        raw = generate(prompt, system=system, json_output=True)
        try:
            return json.loads(clean_json_block(raw))
        except json.JSONDecodeError as exc:
            last_error = exc
    raise GeminiError(f"Could not parse Gemini's JSON response: {last_error}")
