# GitHired — Automated Internship Tracker

A full-stack job tracking app that monitors GitHub repositories for new internship postings, filters for US-only roles, and delivers a consolidated HTML digest email whenever new listings are detected.

**Stack:** Python · Flask · SQLite · APScheduler · BeautifulSoup · React · TypeScript · Tailwind CSS v4

---

## Features

- Scrapes [SimplifyJobs](https://github.com/SimplifyJobs/Summer2026-Internships) README tables on a configurable schedule
- Filters to US-only postings using state abbreviation and keyword detection
- Only surfaces jobs posted within the last 0–1 days — no stale listings
- Sends a single HTML digest email per run instead of one email per job
- React dashboard with job search, date range filters, run history, and manual trigger
- REST API with pagination, filtering by company/role/location/date

---

## Project Structure

```
job-tracker/
├── .env.example          # Copy to .env and fill in your values
├── backend/
│   ├── app/
│   │   ├── __init__.py   # App factory
│   │   ├── config.py     # Env var loading + validation
│   │   ├── db.py         # SQLite helpers
│   │   ├── scraper.py    # GitHub README scraper
│   │   ├── notifier.py   # Gmail digest emails
│   │   ├── scheduler.py  # APScheduler background job
│   │   └── routes.py     # Flask REST API blueprint
│   ├── run.py            # Entry point
│   ├── seed.py           # One-time DB seed (marks existing jobs as notified)
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── pages/        # Dashboard, JobsList, Repos
    │   ├── lib/          # API client + types
    │   └── App.tsx
    └── package.json
```

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- A [GitHub Personal Access Token](https://github.com/settings/tokens) (read-only, public repos)
- A Gmail account with an [App Password](https://myaccount.google.com/apppasswords) enabled (requires 2FA)

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/githired.git
cd githired/job-tracker
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
GITHUB_TOKEN="ghp_yourtoken"
EMAIL_SENDER="you@gmail.com"
EMAIL_PASSWORD="your-app-password"      # Gmail App Password, NOT your account password
EMAIL_RECIPIENT="you@gmail.com"
CHECK_INTERVAL_MINUTES=120              # How often the scraper runs
DATABASE_PATH=jobs.db
FLASK_SECRET_KEY="change-me"
FILTER_COUNTRY=USA                      # Leave blank to skip country filtering
```

### 3. Set up the backend

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Seed the database

This marks all currently listed jobs as already-notified so you don't get flooded with emails on first run:

```bash
python seed.py
```

### 5. Set up the frontend

```bash
cd ../frontend
npm install
```

---

## Running

Open two terminals.

**Terminal 1 — Backend**

```bash
cd backend
.\venv\Scripts\activate   # Windows
python run.py
```

Flask starts on `http://localhost:5000`.

**Terminal 2 — Frontend**

```bash
cd frontend
npm run dev
```

Vite starts on `http://localhost:5173`.

---

## Adding a Repo to Monitor

Once the backend is running, add a repo via the **Repos** page in the UI, or via the API:

```bash
curl -X POST http://localhost:5000/api/repos \
  -H "Content-Type: application/json" \
  -d '{"owner": "SimplifyJobs", "name": "Summer2026-Internships"}'
```

The scheduler will scrape it automatically on the next interval. You can also trigger a manual run from the Dashboard.

---

## API Reference

| Method   | Endpoint        | Description                                                                             |
| -------- | --------------- | --------------------------------------------------------------------------------------- |
| `GET`    | `/api/health`   | App status + total jobs                                                                 |
| `GET`    | `/api/jobs`     | Paginated jobs (`?company=&role=&location=&date_posted=&posted_after=&page=&per_page=`) |
| `GET`    | `/api/jobs/new` | Jobs in a time window (`?min_hours=0&max_hours=24`)                                     |
| `DELETE` | `/api/jobs`     | Clear all jobs                                                                          |
| `GET`    | `/api/repos`    | List monitored repos                                                                    |
| `POST`   | `/api/repos`    | Add a repo `{"owner": "", "name": ""}`                                                  |
| `POST`   | `/api/run`      | Manually trigger a scrape run                                                           |
| `GET`    | `/api/runs`     | Last 20 run log entries                                                                 |

---

## Email Setup (Gmail)

1. Enable 2-Factor Authentication on your Google account
2. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Generate an App Password for "Mail"
4. Use that 16-character password as `EMAIL_PASSWORD` in `.env` — **not** your regular Gmail password
