# ResumeBot

A Telegram bot that analyzes resumes against job descriptions using AI and returns an ATS-style compatibility report.

## How It Works

1. **Start** — Send `/start` to begin. The bot asks for your resume.
2. **Upload Resume** — Send a PDF or DOCX file. The bot extracts the text and stores it.
3. **Paste Job Description** — Paste the job description as text or upload a PDF/DOCX. The bot sends both to an AI model for analysis.
4. **ATS Report** — The AI returns a structured report including:
   - ATS score with per-category breakdown
   - Matching and missing skills
   - Strengths and weaknesses
   - Improvement suggestions
   - Interview readiness estimate
5. **Follow-up Actions** — After the report, you can:
   - Analyze another job description against the same resume
   - Rewrite weak resume bullet points
   - Compare with another resume (coming soon)

## Setup

1. Create a virtual environment and install dependencies:
   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in your keys:
   ```
   cp .env.example .env
   ```

3. Edit `.env`:
   ```
   GROQ_API_KEY=your_groq_api_key
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   ```

4. Run the bot:
   ```
   python main.py
   ```

## Stack

- Python 3.11+
- python-telegram-bot v21+ (async)
- Groq AI (LLM analysis)
- pdfplumber (PDF text extraction)
- python-docx (DOCX text extraction)
