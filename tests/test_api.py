"""API tests. Gemini is mocked, so these run offline and cost nothing."""

import json
import os
import sys

import pytest
from fastapi.testclient import TestClient

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
os.environ["USE_LOCAL_MODEL"] = "false"

import gemini_client  # noqa: E402
import main  # noqa: E402

QUIZ = [
    {"question": "What is a^2 + b^2 equal to in a right triangle?",
     "options": ["c^2", "2c", "c", "ab"], "answer": "c^2", "explanation": "Pythagoras."},
    {"question": "Which side is the hypotenuse?",
     "options": ["Shortest", "Opposite the right angle", "Adjacent", "Any"],
     "answer": "Opposite the right angle"},
    {"question": "3-4-? is a Pythagorean triple", "options": ["5", "6", "7", "8"], "answer": "5"},
]

PATH = {
    "topic": "SQL", "overview": "From queries to optimisation.",
    "stages": [{"title": "Basics", "level": "Beginner", "duration": "1 week",
                "concepts": ["SELECT"], "practice": "Query a table",
                "resources": [{"name": "SQLBolt", "type": "course"}]}],
    "tips": ["Practise daily"],
}


@pytest.fixture
def fake_gemini(monkeypatch):
    calls = {}

    def fake_generate(prompt, system=None, json_output=False):
        calls["prompt"] = prompt
        if json_output:
            return "```json\n" + json.dumps(PATH if "learning path" in prompt else QUIZ) + "\n```"
        return "The Pacific Ocean is the largest ocean."

    monkeypatch.setattr(gemini_client, "generate", fake_generate)
    for mod in ("qna", "summary_module", "explanation_module"):
        monkeypatch.setattr(sys.modules[mod], "generate", fake_generate)
    return calls


@pytest.fixture
def client():
    with TestClient(main.app) as c:
        yield c


def test_home_page(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "EduGenie" in r.text


def test_qa(client, fake_gemini):
    r = client.post("/qa", json={"question": "Which is the largest ocean?"})
    assert r.status_code == 200
    assert "Pacific" in r.json()["answer"]
    assert "Which is the largest ocean?" in fake_gemini["prompt"]


def test_explain_falls_back_to_gemini(client, fake_gemini):
    r = client.post("/explain", json={"concept": "Photosynthesis", "level": "beginner"})
    assert r.status_code == 200
    assert r.json()["source"] == "Gemini"


def test_quiz_parses_fenced_json(client, fake_gemini):
    r = client.post("/quiz", json={"text": "The Pythagoras Theorem"})
    assert r.status_code == 200
    questions = r.json()["questions"]
    assert len(questions) == 3
    for q in questions:
        assert len(q["options"]) == 4 and q["answer"] in q["options"]


def test_summarize(client, fake_gemini):
    r = client.post("/summarize", json={"text": "Rivers flow into oceans. " * 5})
    assert r.status_code == 200
    assert r.json()["summary"]


def test_learning_path(client, fake_gemini):
    r = client.post("/learn/recommendations", json={"topic": "SQL", "level": "beginner"})
    assert r.status_code == 200
    assert r.json()["stages"][0]["title"] == "Basics"


def test_empty_input_rejected(client):
    assert client.post("/qa", json={"question": ""}).status_code == 422


def test_gemini_error_returns_502(client, monkeypatch):
    def boom(*a, **k):
        raise gemini_client.GeminiError("quota exceeded")

    monkeypatch.setattr(sys.modules["qna"], "generate", boom)
    r = client.post("/qa", json={"question": "Hello there?"})
    assert r.status_code == 502
    assert "quota" in r.json()["detail"]


def test_missing_api_key_gives_clear_error(client, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr(gemini_client, "_client", None)
    r = client.post("/qa", json={"question": "Which is the largest ocean?"})
    assert r.status_code == 502
    assert "GEMINI_API_KEY" in r.json()["detail"]


def test_overloaded_model_falls_back(monkeypatch):
    """A 503 on the main model retries, then switches to the fallback model."""
    calls = []

    class FakeModels:
        def generate_content(self, model, contents, config):
            calls.append(model)
            if model == "main-model":
                raise Exception("503 UNAVAILABLE. This model is currently experiencing high demand.")
            return type("R", (), {"text": "ok from fallback"})()

    fake_client = type("C", (), {"models": FakeModels()})()
    monkeypatch.setattr(gemini_client, "_get_client", lambda: fake_client)
    monkeypatch.setattr(gemini_client.time, "sleep", lambda s: None)
    monkeypatch.setenv("GEMINI_MODEL", "main-model")
    monkeypatch.setenv("GEMINI_FALLBACK_MODEL", "backup-model")
    assert gemini_client.generate("hi") == "ok from fallback"
    assert calls == ["main-model"] * 3 + ["backup-model"]


def test_overloaded_everywhere_gives_friendly_error(monkeypatch):
    class FakeModels:
        def generate_content(self, model, contents, config):
            raise Exception("503 UNAVAILABLE")

    monkeypatch.setattr(gemini_client, "_get_client", lambda: type("C", (), {"models": FakeModels()})())
    monkeypatch.setattr(gemini_client.time, "sleep", lambda s: None)
    with pytest.raises(gemini_client.GeminiError, match="overloaded"):
        gemini_client.generate("hi")
