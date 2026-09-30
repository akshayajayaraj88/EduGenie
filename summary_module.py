"""Summarisation of long educational passages with Gemini."""

import prompts
from gemini_client import generate


def summarize_text(text: str) -> str:
    return generate(prompts.SUMMARY.format(text=text), system=prompts.SYSTEM)
