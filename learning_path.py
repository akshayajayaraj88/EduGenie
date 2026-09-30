"""Personalised learning path recommendations with Gemini."""

import prompts
from gemini_client import GeminiError, generate_json


def get_learning_recommendations(topic: str, level: str = "beginner") -> dict:
    data = generate_json(
        prompts.LEARNING_PATH.format(topic=topic, level=level), system=prompts.SYSTEM
    )
    if not isinstance(data, dict) or not data.get("stages"):
        raise GeminiError("The learning path came back incomplete. Please try again.")
    data.setdefault("topic", topic)
    data.setdefault("overview", "")
    data.setdefault("tips", [])
    return data
