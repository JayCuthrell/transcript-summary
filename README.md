# transcript-summary

This repo downloads recent premium podcast episodes from a private Supercast RSS feed, uploads the audio to Google's Gemini API for transcription/analysis, and writes summarized prep notes for your show.

**Quick overview**
- Downloads premium audio from Supercast RSS.
- Uploads audio to Gemini for processing.
- Saves a Markdown prep file to your Google Drive and optionally emails it.

**Prerequisites**
- Python 3.10+ installed
- A Gemini API key and any other credentials in a `.env` file (see below)

**Files of interest**
- `pull-transcripts.py`: main script that downloads audio and calls Gemini.
- `setup.sh`: convenience script to create/activate a venv and install `requirements.txt`.
- `requirements.txt`: runtime dependencies.
 - `process_techmeme.py`: downloads Techmeme's River page, extracts permalink clusters, writes a Markdown digest to `~/My Drive/Podcast/`, and can email the digest if Gmail creds are provided in `.env`.

**Quickstart (automated)**
If you want the simple, one-line approach you already have:

```bash
# create venv, install deps, and activate (existing helper)
source setup.sh
```

**Recommended manual setup (safer & idempotent)**
If you prefer an explicit, reproducible setup:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip wheel
python -m pip install -r requirements.txt
```

**Environment variables (.env)**
Create a `.env` file in the project root with these keys (example):

```
SUPERCAST_MEMBERSHIP_ID=your_supercast_membership_id
GEMINI_API_KEY=wef...         # Google Gemini API key
GMAIL_SENDER=you@example.com   # optional, for email notifications
GMAIL_APP_PASSWORD=app-password
GMAIL_RECIPIENT=me@example.com
```

`pull-transcripts.py` checks for these variables and will raise a clear error if required keys are missing.

**Run the main scripts**

```bash
# Transcribe and summarize podcast episodes via Gemini
python3 pull-transcripts.py

# Fetch Techmeme River permalinks and write a digest (optionally emails it)
python3 process_techmeme.py
```

What to expect from `process_techmeme.py`:
- Downloads Techmeme River, extracts headline permalink clusters, and writes a Markdown file named like `Techmeme_River_Permalinks_YYYYMMDD.md` to `~/My Drive/Podcast/`.
- If Gmail credentials are configured in `.env`, the script will attempt to email the digest to `GMAIL_RECIPIENT`.

**Recommendations & next steps**
- Pin dependency versions for reproducibility (create a `requirements-lock.txt` or use `pip-compile`).
- Consider making `setup.sh` idempotent and using `.venv` instead of recreating `my_env` every time.
- Add a `requirements-dev.txt` for linting/test tools if you add tests.

**Troubleshooting**
- Missing env vars: check `.env` in the repo root.
- Permission errors writing to `~/My Drive/Podcast/`: update `drive_path` or create the directory.
- Gemini or requests errors: check network access and valid API key.

**Contributing**
PRs welcome — please open issues for feature requests and include a short description and reproduction steps.

**License**
This project has no license file; add one if you intend to publish or share broadly.

