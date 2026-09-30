"""Question answering with Gemini."""

import prompts
from gemini_client import generate


def answer_question(question: str) -> str:
    return generate(prompts.QNA.format(question=question), system=prompts.SYSTEM)
