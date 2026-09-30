"""EduGenie: FastAPI app serving the web UI and five AI learning endpoints."""

import logging
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

import explanation_module
from gemini_client import GeminiError, model_name
from learning_path import get_learning_recommendations
from qna import answer_question
from quiz_module import generate_quiz
from summary_module import summarize_text

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

MAX_CHARS = 5000
Level = Literal["beginner", "intermediate", "advanced"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    explanation_module.load_local_model_in_background()
    yield


app = FastAPI(title="EduGenie", description="Gemini-powered learning assistant", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ---------- Request / response models ----------

def text_field(description: str):
    return Field(..., min_length=2, max_length=MAX_CHARS, description=description)


class QARequest(BaseModel):
    question: str = text_field("The student's question")


class ExplainRequest(BaseModel):
    concept: str = text_field("Concept to explain")
    level: Level = "beginner"


class QuizRequest(BaseModel):
    text: str = text_field("A topic or a passage to build the quiz from")


class SummaryRequest(BaseModel):
    text: str = Field(..., min_length=20, max_length=MAX_CHARS * 2)


class LearningPathRequest(BaseModel):
    topic: str = text_field("What the learner wants to learn")
    level: Level = "beginner"


class AnswerResponse(BaseModel):
    answer: str


class ExplainResponse(BaseModel):
    explanation: str
    source: str


class QuizQuestion(BaseModel):
    question: str
    options: list[str]
    answer: str
    explanation: str = ""


class QuizResponse(BaseModel):
    questions: list[QuizQuestion]


class SummaryResponse(BaseModel):
    summary: str


# ---------- Routes ----------

def run(fn, *args):
    """Call a module function and turn AI failures into a clean 502 error."""
    try:
        return fn(*args)
    except GeminiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "gemini_model": model_name(),
        "local_model": explanation_module.local_status(),
    }


@app.post("/qa", response_model=AnswerResponse)
def qa(req: QARequest):
    return {"answer": run(answer_question, req.question.strip())}


@app.post("/explain", response_model=ExplainResponse)
def explain(req: ExplainRequest):
    text, source = run(explanation_module.explain_concept, req.concept.strip(), req.level)
    return {"explanation": text, "source": source}


@app.post("/quiz", response_model=QuizResponse)
def quiz(req: QuizRequest):
    return {"questions": run(generate_quiz, req.text.strip())}


@app.post("/summarize", response_model=SummaryResponse)
def summarize(req: SummaryRequest):
    return {"summary": run(summarize_text, req.text.strip())}


@app.post("/learn/recommendations")
def learn(req: LearningPathRequest):
    return run(get_learning_recommendations, req.topic.strip(), req.level)
