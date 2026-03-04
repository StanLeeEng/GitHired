import sqlite3
from datetime import datetime, timezone


def get_db(db_path: str) -> sqlite3.Connection:
    """Opens connection to SQLite database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db(db_path: str):
    """Create tables if they don't already exist."""
    conn = get_db(db_path)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS jobs (
            id          TEXT PRIMARY KEY,
            company     TEXT NOT NULL,
            role        TEXT NOT NULL,
            location    TEXT,
            link        TEXT,
            repo        TEXT NOT NULL,
            notified    INTEGER DEFAULT 0,
            seen_at     TEXT NOT NULL,
            notified_at TEXT,
            date_posted TEXT
        );

        CREATE TABLE IF NOT EXISTS repos (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            owner    TEXT NOT NULL,
            name     TEXT NOT NULL,
            active   INTEGER DEFAULT 1,
            added_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS run_log (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            repo       TEXT NOT NULL,
            ran_at     TEXT NOT NULL,
            jobs_found INTEGER DEFAULT 0,
            jobs_new   INTEGER DEFAULT 0,
            status     TEXT,
            error_msg  TEXT
        );
    """)
    # Migrate existing DBs that predate the date_posted column
    try:
        conn.execute("ALTER TABLE jobs ADD COLUMN date_posted TEXT")
        conn.commit()
    except Exception:
        pass  # Column already exists
    conn.close()

def find_new_jobs(jobs: list[dict], conn: sqlite3.Connection) -> list[dict]:
    """Filter jobs that are already in the database."""
    new = []
    for job in jobs:
        row = conn.execute(
            "SELECT id FROM jobs WHERE id = ?", (job["id"],)
        ).fetchone()
        if row is None:
            new.append(job)
    return new

def insert_jobs(jobs: list[dict], conn: sqlite3.Connection) -> None:
    for job in jobs:
        conn.execute(
            """INSERT OR IGNORE INTO jobs (id, company, role, location, link, repo, seen_at, date_posted)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                job["id"],
                job["company"],
                job["role"],
                job.get("location", ""),
                job.get("link", ""),
                job["repo"],
                datetime.now(timezone.utc).isoformat(),
                job.get("date_posted", ""),
            ),
        )
    conn.commit()

def log_run(repo: str, jobs_found: int, jobs_new: int, status: str, conn: sqlite3.Connection, error_msg: str | None = None):
    """Records how many times the scraper runs"""
    conn.execute(
        """INSERT INTO run_log (repo, ran_at, jobs_found, jobs_new, status, error_msg)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            repo,
            datetime.now(timezone.utc).isoformat(),
            jobs_found,
            jobs_new,
            status,
            error_msg,
        ),
    )
    conn.commit()