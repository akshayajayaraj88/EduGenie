# EduGenie – Windows Installation and Setup Guide

This guide takes you from a fresh Windows 10 or Windows 11 laptop to EduGenie running in your browser.
No prior Python experience is needed. Follow the steps in order.

**Time needed:** about 20–30 minutes (most of it is downloads).

**What you will install**

| Tool | Why EduGenie needs it | Cost |
| --- | --- | --- |
| Python 3.12 | Runs the EduGenie backend (FastAPI) | Free |
| Git | Downloads the project from GitHub | Free |
| A Google account | To create a Gemini API key | Free |
| A web browser (Chrome, Edge, Firefox) | To use the EduGenie web page | Free |

---

## Contents

1. [Install Python](#step-1--install-python)
2. [Install Git](#step-2--install-git)
3. [Download the EduGenie project](#step-3--download-the-edugenie-project)
4. [Create a virtual environment](#step-4--create-a-virtual-environment)
5. [Install the Python packages](#step-5--install-the-python-packages)
6. [Get a Google Gemini API key](#step-6--get-a-google-gemini-api-key)
7. [Create the .env settings file](#step-7--create-the-env-settings-file)
8. [Run EduGenie](#step-8--run-edugenie)
9. [Open the app in your browser](#step-9--open-the-app-in-your-browser)
10. [Daily use: starting and stopping](#step-10--daily-use-starting-and-stopping)
11. [Optional: the local explanation model](#optional--the-local-explanation-model)
12. [Optional: run the automated tests](#optional--run-the-automated-tests)
13. [Updating the project and pushing changes](#updating-the-project-and-pushing-changes)
14. [Settings reference (.env)](#settings-reference-env)
15. [Troubleshooting](#troubleshooting)

---

## Step 1 – Install Python

EduGenie needs **Python 3.10 or newer**. Python **3.12** is recommended.

1. Open https://www.python.org/downloads/windows/ and download the **Windows installer (64-bit)** for the latest **Python 3.12.x**.
2. Run the downloaded file.
3. **Important:** on the first screen, tick **"Add python.exe to PATH"** at the bottom.
   If you skip this, Windows will not find the `python` command later.
4. Click **Install Now** and wait for it to finish.
5. If you see **"Disable path length limit"**, click it (this avoids errors with long file paths), then **Close**.

**Check it worked.** Open **PowerShell** (press the Windows key, type `PowerShell`, press Enter) and run:

```powershell
python --version
```

You should see something like `Python 3.12.7`.

> If you see `Python was not found; run without arguments to install from the Microsoft Store`, or the
> Microsoft Store opens, see [Troubleshooting → "python is not recognized"](#python-is-not-recognized-or-the-microsoft-store-opens).

---

## Step 2 – Install Git

1. Open https://git-scm.com/download/win. The download starts automatically (choose **64-bit Git for Windows Setup** if asked).
2. Run the installer. The default options are fine: keep clicking **Next**, then **Install**.
3. **Close and reopen PowerShell** so it picks up Git, then check:

```powershell
git --version
```

You should see something like `git version 2.47.0.windows.1`.

> **No Git?** You can instead download the project as a ZIP from GitHub: open
> https://github.com/akshayajayaraj88/EduGenie, click the green **Code** button → **Download ZIP**, and
> extract it to your Documents folder. Then skip to Step 4. (You will not be able to pull updates or push changes without Git.)

---

## Step 3 – Download the EduGenie project

In PowerShell, go to the folder where you want the project (Documents is a good choice) and clone it:

```powershell
cd $HOME\Documents
git clone https://github.com/akshayajayaraj88/EduGenie.git
cd EduGenie
```

Check you are in the right folder:

```powershell
dir
```

You should see `main.py`, `requirements.txt`, `.env.example`, and the folders `static`, `templates`, `tests` and `docs`.

> **Tip:** Avoid putting the project inside a OneDrive-synced folder if you can. OneDrive can lock files
> while syncing and slow down package installs. `C:\Users\<you>\Documents` is fine when OneDrive backup
> of Documents is off; otherwise use a folder like `C:\Projects`.

---

## Step 4 – Create a virtual environment

A virtual environment ("venv") keeps EduGenie's packages separate from the rest of your computer.

Still in the `EduGenie` folder, run:

```powershell
python -m venv .venv
```

This creates a `.venv` folder. Now **activate** it:

```powershell
.venv\Scripts\Activate.ps1
```

When it works, your prompt starts with `(.venv)`, for example:

```
(.venv) PS C:\Users\you\Documents\EduGenie>
```

> **Red error "running scripts is disabled on this system"?** Windows blocks the activation script by default.
> Run this once, type `Y` if asked, then activate again:
>
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> .venv\Scripts\Activate.ps1
> ```
>
> **Using Command Prompt (cmd) instead of PowerShell?** Activate with `.venv\Scripts\activate.bat`.

**You must activate the venv every time you open a new PowerShell window** to work on EduGenie.

---

## Step 5 – Install the Python packages

With `(.venv)` showing in your prompt, run:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

This installs FastAPI, Uvicorn, Jinja2, python-dotenv, Pydantic and the Google Gen AI SDK (`google-genai`).
It takes 1–3 minutes. The last line should start with `Successfully installed ...`.

---

## Step 6 – Get a Google Gemini API key

EduGenie uses Google's Gemini models to answer questions, make quizzes, summarise text and build learning paths.
It needs an **API key** — a secret password that lets the app use Gemini on your behalf.

1. Open **Google AI Studio**: https://aistudio.google.com/apikey
2. Sign in with your Google account and accept the terms if asked.
3. Click **Create API key**.
   - If asked to choose a Google Cloud project, pick the default one or click **Create API key in new project**.
4. Copy the key. It is a long string that usually starts with `AIza`.

**Keep this key private.**

- Never paste it into chats, emails, screenshots or code.
- Never upload it to GitHub (EduGenie's `.gitignore` already keeps the `.env` file out of Git).
- If it leaks, delete it in AI Studio and create a new one.

**Free tier:** Google offers a free tier with rate limits (a certain number of requests per minute and per day).
That is plenty for learning and testing. If you hit the limit you will see a "usage limit reached" message —
wait a minute and try again. Current limits are listed at https://ai.google.dev/gemini-api/docs/rate-limits.

---

## Step 7 – Create the .env settings file

EduGenie reads your API key and settings from a file called `.env` in the project folder.
A template called `.env.example` is included.

1. Copy the template (in PowerShell, inside the `EduGenie` folder):

   ```powershell
   copy .env.example .env
   ```

2. Open it in Notepad:

   ```powershell
   notepad .env
   ```

3. Replace `your-api-key-here` with your real key. No quotes, no spaces:

   ```
   GEMINI_API_KEY=AIzaSyYourRealKeyGoesHere
   ```

4. Leave the other lines as they are for now, then **File → Save** and close Notepad.

**Check the file name is exactly `.env`** (not `.env.txt`):

```powershell
dir -Force .env*
```

You should see both `.env` and `.env.example`. If you see `.env.txt`, rename it:

```powershell
ren .env.txt .env
```

> **Why the check?** When saving from Notepad's "Save As" box, Windows sometimes adds `.txt` to the name,
> and File Explorer hides file extensions by default. Using `copy` and `notepad .env` as above avoids this.

---

## Step 8 – Run EduGenie

Make sure you are in the `EduGenie` folder with `(.venv)` showing, then start the server:

```powershell
python -m uvicorn main:app --reload
```

After a few seconds you should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [...]
INFO:     Application startup complete.
```

**Leave this window open.** EduGenie runs only while this window is running. You will also see a line in this
window every time the app calls Gemini, for example `gemini-3.8-flash answered in 2.1s` — useful for troubleshooting.

> **Windows Security / Firewall pop-up?** If Windows asks whether to allow Python on networks, you can click
> **Cancel** or **Allow** — EduGenie only runs on your own computer (`127.0.0.1`), so either is fine.

---

## Step 9 – Open the app in your browser

Open your browser and go to:

**http://127.0.0.1:8000** (or http://localhost:8000)

You should see the EduGenie page with a task dropdown, a text box and a **Submit** button.

**Quick test:** choose **Ask a question**, type `Which is the largest ocean?`, and click **Submit**.
After a few seconds the answer (the Pacific Ocean) appears below the form.

Two other useful pages:

| Address | What it shows |
| --- | --- |
| http://127.0.0.1:8000/health | Which Gemini model is configured and whether the local model is loaded |
| http://127.0.0.1:8000/docs | Interactive API documentation — try every endpoint directly |

**How to use each feature** is explained in the [User Guide](USER_GUIDE.md).

---

## Step 10 – Daily use: starting and stopping

**To stop EduGenie:** click the PowerShell window where it is running and press **Ctrl + C**.

**To start it again later:**

```powershell
cd $HOME\Documents\EduGenie
.venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload
```

Then open http://127.0.0.1:8000.

**After editing `.env`**, always stop (Ctrl + C) and start the server again — the settings are read only at start-up.

---

## Optional – The local explanation model

The original EduGenie design uses a small offline model, **LaMini-Flan-T5-783M**, for the **Explain a concept** feature.
It is **off by default** because it needs a large download (about 3 GB including PyTorch) and a few GB of free RAM.
Without it, explanations come from Gemini, which works well.

To turn it on:

1. With the venv active, install the extra packages:

   ```powershell
   pip install -r requirements-local.txt
   ```

2. In `.env`, change the last line to:

   ```
   USE_LOCAL_MODEL=true
   ```

3. Restart the server. The first start downloads the model from Hugging Face (several minutes).
   The PowerShell window shows `Local explanation model ready.` when it has loaded.

Until it is ready, or if it fails to load, EduGenie automatically uses Gemini for explanations.
Each explanation shows which model answered ("Answered by LaMini-Flan-T5 (local)" or "Answered by Gemini").

> On Windows the model runs on the CPU, which is fine for this small model. If you have an NVIDIA GPU and
> installed the CUDA build of PyTorch, EduGenie uses the GPU automatically.

---

## Optional – Run the automated tests

The tests check every endpoint. Gemini is simulated, so they run offline and do not use your API quota.

```powershell
pip install -r requirements-dev.txt
python -m pytest -q
```

You should see all tests passing, for example `11 passed`.

---

## Updating the project and pushing changes

**Get the latest version from GitHub:**

```powershell
cd $HOME\Documents\EduGenie
git pull
pip install -r requirements.txt
```

**Set your Git name and email (once per computer):**

```powershell
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

**Save and upload your own changes** (you need write access to the GitHub repository):

```powershell
git add .
git commit -m "Describe what you changed"
git push
```

The first time you push, Git for Windows opens a **browser sign-in window** for GitHub — sign in with the
account that owns or has access to the repository. You do not need to create a token.

**Before every commit, check that `.env` is not listed** in `git status`. It should never be uploaded.

---

## Settings reference (.env)

| Setting | Default | What it does |
| --- | --- | --- |
| `GEMINI_API_KEY` | *(none – required)* | Your Gemini API key from Google AI Studio |
| `GEMINI_MODEL` | `gemini-3.8-flash` | Main Gemini model. See https://ai.google.dev/gemini-api/docs/models for current names |
| `GEMINI_FALLBACK_MODEL` | `gemini-3.5-flash-lite` | Used automatically if the main model is overloaded. Set to `none` to disable |
| `GEMINI_TIMEOUT` | `45` | Seconds to wait for Gemini before showing an error |
| `GEMINI_THINKING` | `low` | How much Gemini "thinks" before answering: `minimal`, `low`, `medium`, `high`. Higher is slower but can be more thorough |
| `USE_LOCAL_MODEL` | `false` | `true` uses the offline LaMini-Flan-T5 model for explanations (needs `requirements-local.txt`) |
| `LOCAL_MODEL_ID` | `MBZUAI/LaMini-Flan-T5-783M` | Hugging Face model used when `USE_LOCAL_MODEL=true` |

Restart the server after changing any setting.

---

## Troubleshooting

Errors from the app appear in red on the web page after **"Something went wrong."**
More detail is shown in the PowerShell window where the server is running.

### "python is not recognized" or the Microsoft Store opens

Python was installed without **Add python.exe to PATH**, or Windows' Store shortcut is getting in the way.

- Try the Python launcher instead: `py --version`. If that works, use `py` wherever this guide says `python`
  (for example `py -m venv .venv`).
- Or re-run the Python installer → **Modify** → **Next** → tick **Add Python to environment variables** → **Install**.
- To stop the Store from opening: Windows Settings → **Apps → Advanced app settings → App execution aliases**
  → turn **off** both `python.exe` and `python3.exe` entries for "App Installer".
- Close and reopen PowerShell after any change.

### "running scripts is disabled on this system"

See the note in [Step 4](#step-4--create-a-virtual-environment): run
`Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`, then activate again.

### "No module named uvicorn" / "No module named fastapi"

The virtual environment is not active, or the packages were not installed. Check that your prompt starts with `(.venv)`:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### "Error loading ASGI app. Could not import module 'main'" or "Directory 'static' does not exist"

You started the server from the wrong folder. Go to the project folder first:

```powershell
cd $HOME\Documents\EduGenie
python -m uvicorn main:app --reload
```

### "GEMINI_API_KEY is not set"

- The `.env` file is missing, named `.env.txt`, or not in the `EduGenie` folder — see [Step 7](#step-7--create-the-env-settings-file).
- You edited `.env` while the server was running — stop it with Ctrl + C and start it again.

### "Your Gemini API key is not valid"

The key was copied incompletely or has extra spaces or quotes. Open `.env` with `notepad .env`, paste the key again
so the line reads exactly `GEMINI_API_KEY=AIza...`, save, and restart the server.

### "Gemini is overloaded right now (high demand)" (503)

This comes from Google, not from your setup. EduGenie already retries twice and then switches to the fallback model.
If you still see it, wait a minute and try again, or set `GEMINI_MODEL=gemini-3.5-flash-lite` in `.env` and restart.

### "Gemini usage limit reached" (429)

You have hit the free-tier rate limit. Wait a minute (or until the next day for daily limits) and try again.
Using `gemini-3.5-flash-lite` often gives more free requests.

### "Model ... was not found" (404)

Google has retired or renamed that model. Pick a current model name from
https://ai.google.dev/gemini-api/docs/models, put it in `GEMINI_MODEL` in `.env`, and restart.

### "Gemini did not answer within 45 seconds"

Check your internet connection. Office or college networks sometimes block Google APIs — try another network
or a phone hotspot. You can also raise `GEMINI_TIMEOUT` in `.env`.

### The page keeps showing "EduGenie is thinking…"

Look at the PowerShell window running the server for the latest error line. After 2 minutes the page stops
waiting and shows a message. If it says it **can't reach the EduGenie server**, the server window was closed or
stopped — start it again (Step 10).

### "[Errno 10048] ... address already in use" / port 8000 is busy

Another program (or another EduGenie window) is using port 8000. Close the other window, or run EduGenie on a different port:

```powershell
python -m uvicorn main:app --reload --port 8001
```

Then open http://127.0.0.1:8001.

### "String should have at least 20 characters"

The **Summarise** feature needs a passage of at least 20 characters; other features need at least 2.
Inputs are limited to 5,000 characters (10,000 for summaries).

### "Unable to create ... .git/index.lock: File exists"

A previous Git command was interrupted. If no other Git command is running, delete the lock file and try again:

```powershell
del .git\index.lock
```

### "Permission to ... denied" (403) when pushing

You are signed in to GitHub with an account that cannot write to the repository. Open
**Control Panel → Credential Manager → Windows Credentials**, remove the entries for `git:https://github.com`,
then `git push` again and sign in with the correct account in the browser window.
