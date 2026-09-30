# EduGenie – User Guide

EduGenie is an AI learning assistant powered by Google Gemini. This guide explains how to use each feature.
If EduGenie is not installed yet, follow the [Windows Setup Guide](WINDOWS_SETUP.md) first.

Open the app at **http://127.0.0.1:8000** while the server is running.

---

## The screen

| Part | What it is for |
| --- | --- |
| **What would you like to do?** | Choose one of the five features |
| **Your level** | Beginner, Intermediate or Advanced. Shown only for *Explain a concept* and *Recommend a learning path* |
| **Text box** | Type your question, topic or passage. The counter shows how many characters you have typed |
| **Submit** | Sends your request. The button is disabled while EduGenie is thinking |
| **Result area** | Appears below the form with the answer |

Answers usually take 2–10 seconds. While you wait you will see **"EduGenie is thinking…"**.

---

## 1. Ask a question

Get a short, direct answer to any general-knowledge or school question.

1. Choose **Ask a question**.
2. Type your question, for example: `Which is the largest ocean?`
3. Click **Submit**.

**Result:** a 2–4 sentence answer with the direct answer first.

**Tips:** Ask one question at a time. Be specific — "What causes tides on Earth?" gets a better answer than "tides".

---

## 2. Explain a concept

Get a simple explanation of a topic, with an everyday example.

1. Choose **Explain a concept**.
2. Pick **Your level** (Beginner gives the simplest language).
3. Type the concept, for example: `Photosynthesis` or `Recursion in programming`.
4. Click **Submit**.

**Result:** a short explanation (under about 150 words) in plain language. The line
**"Answered by …"** at the bottom shows whether Gemini or the optional local model wrote it.

---

## 3. Generate a quiz

Test yourself with three multiple-choice questions.

1. Choose **Generate a quiz**.
2. Type a **topic** (for example `The Pythagoras Theorem`) **or paste a passage** from your notes or textbook.
3. Click **Submit**.

**Result:** 3 questions, each with 4 options.

- Click the option you think is right.
- A correct answer turns **green**. A wrong answer turns **red** and the correct option is highlighted in green.
- A one-line explanation appears under each question.
- Your **score** updates at the bottom, and shows "quiz complete!" when all three are answered.

To try new questions on the same topic, click **Submit** again — each quiz is freshly generated.

---

## 4. Summarise a passage

Turn a long paragraph or article into quick revision notes.

1. Choose **Summarise a passage**.
2. Paste the text (at least 20 characters, up to 10,000).
3. Click **Submit**.

**Result:** a one-sentence overview followed by 3–6 bullet points of the key facts.

**Tip:** Paste plain text. Very long chapters work best split into sections.

---

## 5. Recommend a learning path

Get a step-by-step plan to learn a subject from beginner to advanced.

1. Choose **Recommend a learning path**.
2. Pick **Your level** — the plan starts from where you are.
3. Type what you want to learn, for example: `SQL` or `Machine learning`.
4. Click **Submit**.

**Result:**

- A short overview of the path.
- 3–5 **stages**, each with a level badge (Beginner / Intermediate / Advanced), a time estimate,
  key concepts to learn, a small practice task, and 1–2 suggested resources (videos, articles, books, courses or documentation).
- A list of study **tips** at the end.

> Resources are suggested by the AI. Search for them by name; if one no longer exists, look for a similar one.

---

## Good to know

- **AI answers can be wrong.** EduGenie is a study helper, not a replacement for your teacher or textbook.
  Check important facts, especially for exams.
- **Your text is sent to Google Gemini** to generate answers. Do not paste passwords or personal information.
- **Limits:** questions, concepts and topics can be up to 5,000 characters; passages to summarise up to 10,000.
- **Free-tier limits:** with a free Gemini API key you can make a limited number of requests per minute and per day.
  If you see "usage limit reached", wait a minute and try again.
- **Errors** appear in red after "Something went wrong." — see
  [Troubleshooting](WINDOWS_SETUP.md#troubleshooting) for what each message means.

---

## For developers: using the API directly

Every feature is also a JSON API. Open **http://127.0.0.1:8000/docs** to try them in the browser.

| Feature | Method and path | Request body (JSON) | Response |
| --- | --- | --- | --- |
| Ask a question | `POST /qa` | `{"question": "Which is the largest ocean?"}` | `{"answer": "..."}` |
| Explain a concept | `POST /explain` | `{"concept": "Photosynthesis", "level": "beginner"}` | `{"explanation": "...", "source": "Gemini"}` |
| Generate a quiz | `POST /quiz` | `{"text": "The Pythagoras Theorem"}` | `{"questions": [{"question", "options", "answer", "explanation"}]}` |
| Summarise | `POST /summarize` | `{"text": "<passage>"}` | `{"summary": "..."}` |
| Learning path | `POST /learn/recommendations` | `{"topic": "SQL", "level": "beginner"}` | `{"topic", "overview", "stages": [...], "tips": [...]}` |
| Health check | `GET /health` | – | `{"status": "ok", "gemini_model": "...", "local_model": "disabled"}` |

`level` can be `beginner`, `intermediate` or `advanced`.

**Example from PowerShell:**

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/qa `
  -ContentType "application/json" `
  -Body '{"question": "Which is the largest ocean?"}'
```

Errors return HTTP **422** for invalid input (for example, empty text) and **502** when Gemini fails,
with the reason in the `detail` field.
