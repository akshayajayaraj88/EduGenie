# EduGenie Documentation

| Guide | Read it when you want to… |
| --- | --- |
| [Windows Setup Guide](WINDOWS_SETUP.md) | Install Python and Git, get a Google Gemini API key, and run EduGenie on a Windows laptop — plus troubleshooting |
| [User Guide](USER_GUIDE.md) | Learn how to use each feature: questions, explanations, quizzes, summaries and learning paths |

**Quick start (Windows PowerShell)** — for people who already have Python 3.10+ and Git:

```powershell
git clone https://github.com/akshayajayaraj88/EduGenie.git
cd EduGenie
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
notepad .env          # paste your Gemini API key, save, close
python -m uvicorn main:app --reload
```

Then open http://127.0.0.1:8000.

macOS and Linux users can follow the same steps with `source .venv/bin/activate`
and `cp .env.example .env` — see the project [README](../README.md).
