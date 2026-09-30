# EduGenie – Gemini-Powered Learning Assistant

EduGenie is a lightweight AI learning assistant built with FastAPI and a plain HTML/CSS/JS frontend.

| Feature | Endpoint | Model |
| --- | --- | --- |
| Ask a question | `POST /qa` | Gemini |
| Explain a concept | `POST /explain` | LaMini-Flan-T5 (local, optional) with Gemini fallback |
| Generate a quiz (3 MCQs) | `POST /quiz` | Gemini (JSON output) |
| Summarise a passage | `POST /summarize` | Gemini |
| Learning path | `POST /learn/recommendations` | Gemini (JSON output) |

## Documentation

- **Windows users:** step-by-step [Windows Setup Guide](docs/WINDOWS_SETUP.md), including the Gemini API key and troubleshooting
- **How to use EduGenie:** [User Guide](docs/USER_GUIDE.md)

## Setup (Mac M1 or any machine with Python 3.10+)

```bash
cd EduGenie
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # then paste your key into .env
```

Get a free API key from [Google AI Studio](https://aistudio.google.com/apikey) and set `GEMINI_API_KEY` in `.env`.
`GEMINI_MODEL` defaults to `gemini-3.8-flash`; use any current model from the
[Gemini models list](https://ai.google.dev/gemini-api/docs/models). If it is overloaded, EduGenie retries and then
switches to `GEMINI_FALLBACK_MODEL` (default `gemini-3.5-flash-lite`). All settings are listed in the
[settings reference](docs/WINDOWS_SETUP.md#settings-reference-env).

## Run

```bash
uvicorn main:app --reload
```

Open http://127.0.0.1:8000 for the app, or http://127.0.0.1:8000/docs to try the API directly.
`GET /health` shows which Gemini model is configured and whether the local model is loaded.

## Optional: local explanation model

The project brief uses LaMini-Flan-T5-783M for explanations. It is off by default because it needs a
~3 GB download. To turn it on:

```bash
pip install -r requirements-local.txt
# in .env
USE_LOCAL_MODEL=true
```

The model loads in the background at startup (on the M1 GPU via `mps` when available). Until it is ready,
or if it fails, `/explain` uses Gemini, and the answer says which model produced it.

## Tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

Tests mock Gemini, so they run offline and don't use your quota.

## Project structure

```
main.py                FastAPI app, request models, routes
gemini_client.py       Shared Gemini client, JSON parsing (clean_json_block)
prompts.py             All prompt templates
qna.py                 Question answering
explanation_module.py  Local LaMini model + Gemini fallback
quiz_module.py         MCQ generation and validation
summary_module.py      Summarisation
learning_path.py       get_learning_recommendations()
templates/index.html   Web page
static/style.css       Styling
static/app.js          fetch() calls, interactive quiz, learning-path view
tests/test_api.py      API tests with mocked Gemini
```
