"""Shared Google Gemini client used by every cloud-backed module."""

import json
import logging
import os
import re
import time

from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "gemini-3.8-flash"
TIMEOUT_SECONDS = int(os.getenv("GEMINI_TIMEOUT", "45"))
# low = faster answers; set GEMINI_THINKING=high for harder reasoning
THINKING_LEVEL = os.getenv("GEMINI_THINKING", "low").upper()

log = logging.getLogger("edugenie.gemini")


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

        from google.genai import types

        _client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=TIMEOUT_SECONDS * 1000),
        )
    return _client


def model_name() -> str:
    return os.getenv("GEMINI_MODEL", DEFAULT_MODEL)


def fallback_model() -> str:
    """Model to switch to when the main one is overloaded (set to 'none' to disable)."""
    return os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.5-flash-lite")


# Errors that are temporary on Google's side and worth retrying.
RETRYABLE = ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "500", "INTERNAL", "overloaded")


def _is_retryable(exc: Exception) -> bool:
    text = f"{type(exc).__name__} {exc}"
    return any(code in text for code in RETRYABLE)


def _friendly(exc: Exception) -> str:
    text = str(exc)
    if "timed out" in text.lower() or "timeout" in type(exc).__name__.lower():
        return (f"Gemini did not answer within {TIMEOUT_SECONDS} seconds. "
                "Check your internet connection and try again.")
    if "503" in text or "UNAVAILABLE" in text:
        return "Gemini is overloaded right now (high demand). Please try again in a minute."
    if "429" in text or "RESOURCE_EXHAUSTED" in text:
        return "Gemini usage limit reached. Wait a minute, then try again."
    if "API_KEY_INVALID" in text or "API key not valid" in text:
        return "Your Gemini API key is not valid. Check GEMINI_API_KEY in .env."
    if "404" in text or "NOT_FOUND" in text:
        return f"Model '{model_name()}' was not found. Set GEMINI_MODEL in .env to a current model."
    return f"Gemini request failed: {text}"


def _config(model: str, system: str | None, json_output: bool):
    from google.genai import types

    thinking = None
    if model.startswith("gemini-3") and THINKING_LEVEL in {"MINIMAL", "LOW", "MEDIUM", "HIGH"}:
        thinking = types.ThinkingConfig(thinking_level=THINKING_LEVEL)
    return types.GenerateContentConfig(
        system_instruction=system,
        temperature=0.4,
        response_mime_type="application/json" if json_output else None,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        thinking_config=thinking,
    )


def generate(prompt: str, system: str | None = None, json_output: bool = False) -> str:
    """Send a prompt to Gemini and return the response text.

    Temporary errors (overloaded, rate limited) are retried twice with a short pause,
    then the request switches to the fallback model.
    """
    client = _get_client()
    models = [model_name()]
    if fallback_model().lower() not in {"", "none", model_name()}:
        models.append(fallback_model())

    last_exc = None
    for model in models:
        for attempt in range(3):
            start = time.monotonic()
            log.info("Calling %s (attempt %d) ...", model, attempt + 1)
            try:
                response = client.models.generate_content(
                    model=model, contents=prompt, config=_config(model, system, json_output)
                )
            except Exception as exc:
                last_exc = exc
                log.warning("%s failed after %.1fs: %s", model, time.monotonic() - start, exc)
                if not _is_retryable(exc):
                    raise GeminiError(_friendly(exc)) from exc
                if attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
                continue
            log.info("%s answered in %.1fs", model, time.monotonic() - start)
            text = (getattr(response, "text", None) or "").strip()
            if not text:
                raise GeminiError("Gemini returned an empty response. Please try again.")
            return text
        if len(models) > 1 and model == models[0]:
            log.warning("Switching to fallback model %s", models[1])

    raise GeminiError(_friendly(last_exc)) from last_exc


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
