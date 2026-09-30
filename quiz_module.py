"""Quiz generation: multiple-choice questions as validated JSON."""

import prompts
from gemini_client import GeminiError, generate_json


def _valid(question: dict) -> bool:
    options = question.get("options")
    return (
        isinstance(question.get("question"), str)
        and isinstance(options, list)
        and len(options) == 4
        and question.get("answer") in options
    )


def generate_quiz(text: str, count: int = 3) -> list[dict]:
    data = generate_json(
        prompts.QUIZ.format(text=text, count=count), system=prompts.SYSTEM
    )
    if isinstance(data, dict):  # tolerate {"questions": [...]}
        data = data.get("questions", [])
    questions = [q for q in data if isinstance(q, dict) and _valid(q)]
    if not questions:
        raise GeminiError("The quiz came back in an unexpected format. Please try again.")
    for q in questions:
        q.setdefault("explanation", "")
    return questions[:count]
