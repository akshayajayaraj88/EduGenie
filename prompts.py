"""All prompt templates in one place, so they are easy to tune."""

SYSTEM = (
    "You are EduGenie, a friendly learning assistant for students of all levels. "
    "Be accurate, clear and encouraging. If you are not sure of a fact, say so."
)

QNA = """Answer the student's question in 2-4 short sentences.
Give the direct answer first, then one helpful supporting detail.

Question: {question}"""

EXPLAIN = """Explain the concept below to a {level} learner.
Use simple words, avoid jargon, and include one everyday example or analogy.
Keep it under 150 words.

Concept: {concept}"""

# Shorter prompt for the small local LaMini-Flan-T5 model.
EXPLAIN_LOCAL = "Explain {concept} in simple words for a {level} student, with an example."

QUIZ = """Create exactly {count} multiple-choice questions that test understanding of the
topic or passage below. Each question has exactly 4 options, one correct answer,
and plausible distractors. Add a one-sentence explanation of the correct answer.

Return ONLY a JSON array in this shape:
[{{"question": "...", "options": ["...", "...", "...", "..."], "answer": "<exact text of the correct option>", "explanation": "..."}}]

Topic or passage:
{text}"""

SUMMARY = """Summarise the passage below for quick revision.
Start with a one-sentence overview, then 3-6 bullet points of the key facts.
Keep all important information and drop repetition. Use plain text bullets ("- ").

Passage:
{text}"""

LEARNING_PATH = """Create a structured learning path for a {level} learner who wants to learn "{topic}".
Organise it from beginner to advanced in 3-5 stages. For each stage give a time estimate,
the key concepts, a small practice task, and 1-2 well-known free resources (name the resource
and its type: video, article, book, course or documentation).

Return ONLY JSON in this shape:
{{"topic": "...", "overview": "...", "stages": [{{"title": "...", "level": "Beginner|Intermediate|Advanced", "duration": "...", "concepts": ["..."], "practice": "...", "resources": [{{"name": "...", "type": "..."}}]}}], "tips": ["..."]}}"""
