````markdown
# 🤖 Naukri Job Application Bot

Automated job application bot for **Naukri.com** that searches, scores, and applies to jobs automatically.

**No paid APIs needed** - Uses only free libraries: Playwright, BeautifulSoup, Requests

---

## 🎯 What This Bot Does

The bot executes a **4-step pipeline**:

1. **🔍 SCRAPE**: Searches Naukri.com for jobs matching your keywords and location
2. **📊 SCORE**: Scores jobs 0-100 based on keyword relevance (no AI API required)
3. **🔎 FILTER**: Keeps only high-relevance jobs (configurable score threshold)
4. **✅ APPLY**: Auto-applies to filtered jobs with form-filling and resume upload

---

## 📋 Features

- ✅ Login automation with cookie-based session persistence
- ✅ Keyword-based job scoring (no external APIs)
- ✅ Resume auto-upload
- ✅ Form auto-filling (name, phone, skills, etc.)
- ✅ Duplicate application prevention (tracks applied jobs)
- ✅ Error handling and graceful failure (never crashes)
- ✅ Realistic delays to avoid bot detection
- ✅ Detailed logging (both file and console)
- ✅ Customizable search queries, location, experience level
- ✅ Browser visibility toggle (headless mode)

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/Rohitmehraji/naukri_jobbot.git
cd naukri_jobbot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Configure Environment

Copy `.env.example` to `.env` and fill in your details:

```bash
cp .env.example .env
```

Edit `.env`:

```env
NAUKRI_EMAIL=your_email@gmail.com
NAUKRI_PASSWORD=your_password
RESUME_PATH=resume.pdf
CANDIDATE_NAME=Your Full Name
CANDIDATE_PHONE=+91-XXXXXXXXXX
```

### 4. Run the Bot

```bash
python bot.py
```

The browser will open automatically (watch it apply!). Set `headless: True` in `config.py` to hide the browser.

---

## 📁 Project Structure

```
naukri_jobbot/
├── bot.py                 # Main orchestrator (4-step pipeline)
├── config.py              # Configuration & settings
├── scraper.py             # Naukri.com job scraper
├── applier.py             # Playwright browser automation
├── scorer.py              # Keyword-based job scoring
├── logger_setup.py        # Logging configuration
├── requirements.txt       # Python dependencies
├── .env.example            # Environment template
├── .env                   # Your credentials (DO NOT COMMIT)
├── logs/                  # Output directory
│   ├── run_TIMESTAMP.log  # Detailed logs from each run
│   ├── cookies.json       # Browser cookies (session persistence)
│   ├── applied_jobs.json  # Record of applied jobs
│   └── .gitkeep
└── resume.pdf             # Your resume file
```

---

## ⚙️ Configuration

Edit `config.py` to customize:

```python
CONFIG = {
    "search_queries": ["AI Engineer", "ML Engineer", "Python Developer"],
    "location": "Indore",
    "experience": "0-2",
    "min_score": 30,          # Minimum relevance score (0-100)
    "max_applications": 20,   # Max jobs to apply to per run
    "delay_seconds": 3,       # Delay between applications
    "headless": False,        # Set True to hide browser
}
```

---

## 🧠 How Job Scoring Works

**No AI API required!** Jobs are scored using simple keyword matching:

- Each matching skill keyword = +8 points (max 100)
- Matches searched in job title + description
- Skill keywords include: Python, ML, AI, LangChain, FastAPI, FAISS, etc.

Example:
- Job title: "Python ML Engineer" + Description: "Experience with LangChain and FAISS required"
- Matched keywords: python, ml, langchain, faiss
- Score: 4 × 8 = 32/100

---

## 📊 Sample Output

```
============================================================
NAUKRI JOB APPLICATION BOT - STARTING
============================================================
Configuration:
  Search Queries: ['AI Engineer', 'ML Engineer', 'Python Developer', 'LLM Engineer']
  Location: Indore
  Min Score: 30
  Max Applications: 20
============================================================
[STEP 1] SCRAPING JOBS FROM NAUKRI.COM
------------------------------------------------------------
Searching: 'AI Engineer' in Indore
  Found 45 jobs
Searching: 'ML Engineer' in Indore
  Found 52 jobs
Total unique jobs scraped: 89
------------------------------------------------------------
[STEP 2] SCORING JOBS (KEYWORD MATCHING)
Scoring complete
------------------------------------------------------------
[STEP 3] FILTERING JOBS BY RELEVANCE
Filtered 89 → 18 jobs (score >= 30)
Top jobs to apply for:
  1. [88/100] Senior ML Engineer @ TechCorp India
     Matched 11 skills: python, machine learning, ml, fastapi, ...
  2. [72/100] AI Backend Developer @ StartupXYZ
     Matched 9 skills: python, ai, docker, api, ...
  3. [64/100] Python Engineer @ DataFlow Systems
     Matched 8 skills: python, sql, etl, data engineer, ...
------------------------------------------------------------
[STEP 4] APPLYING TO JOBS
→ Applying to: Senior ML Engineer
  ✓ Applied successfully
→ Applying to: AI Backend Developer
  ✓ Applied successfully
============================================================
APPLICATIONS COMPLETED
  Applied: 18
  Skipped: 0
  Total: 18
============================================================
```

---

## 🔐 Security & Privacy

- ✅ Credentials stored in `.env` (never committed to git)
- ✅ Cookies saved locally (no cloud storage)
- ✅ Applied jobs tracked locally (privacy by design)
- ✅ No data sent to external servers
- ⚠️ Resume uploaded directly to Naukri.com only

Add to `.gitignore`:
```
.env
logs/cookies.json
logs/applied_jobs.json
logs/*.log
resume.pdf
```

---

## 🐛 Troubleshooting

### "Login failed"
- Verify email/password in `.env` are correct
- Try `headless: False` to see login process
- Check if Naukri requires 2FA (disable temporarily)
- Clear `logs/cookies.json` to force fresh login

### "No Apply button found"
- Job may require manual application
- Already applied to that job (check `logs/applied_jobs.json`)
- Resume may be missing or incorrect format

### "Bot detection / Captcha"
- Set `headless: False` to manually solve captcha
- Increase `delay_seconds` to slow down applications
- Reduce `max_applications` per run

### "Resume not uploading"
- Verify `RESUME_PATH` is correct and file exists
- File format should be `.pdf`
- Use relative path from project root

### Getting "0" jobs from scraper
- Naukri may have updated HTML structure
- Try searching with different keywords
- Check logs for specific error messages

---

## 📝 Logging

Logs are saved to `logs/run_TIMESTAMP.log` with format:
```
2026-06-07 14:30:45 [INFO   ] Job scored: 72/100 - Matched 9 skills: python, ml, fastapi...
2026-06-07 14:30:46 [DEBUG  ] Email filled
2026-06-07 14:30:47 [INFO   ] ✓ Login successful
2026-06-07 14:31:05 [INFO   ] → Applying to: Senior ML Engineer
2026-06-07 14:31:08 [INFO   ]   Resume uploaded
2026-06-07 14:31:12 [INFO   ]   ✓ Applied successfully
```

---

## 📌 Important Notes

- 🚫 **Do not commit `.env` file** - add to `.gitignore`
- 🔄 **Resume file must exist** before running
- ⏱️ **Realistic delays** prevent Naukri from blocking you
- 💾 **`applied_jobs.json` persists** across runs (no duplicates)
- 📋 **Cookie-based login** skips repeated login on next run
- ⚠️ **Use responsibly** - respect Naukri's terms of service

---

## 🎓 How to Use This Project

1. **First Run**: Bot will login, scrape, score, and apply
2. **Subsequent Runs**: Bot loads cookies (skip login) and applies to new jobs
3. **Check Logs**: Review `logs/run_*.log` for detailed execution info
4. **Track Applications**: See `logs/applied_jobs.json` for all applied jobs

---

## 🤝 Contributing

Found an issue? Fork and submit a PR! 

Suggestions for improvement:
- Support for Indeed.com
- Better job scoring (optional ML model)
- Scheduled runs (cron jobs)
- Email notifications

---

## ⚖️ Legal

This bot is for **educational purposes**. Ensure compliance with:
- Naukri.com Terms of Service
- Local labor laws
- Platform usage policies

---

## 📧 Contact

Questions? Open an issue on GitHub!

---

## 🎉 Good Luck!

May your applications lead to amazing opportunities! 🚀

````
