from app.scraper import scrape_repo
from app.db import get_db, init_db
from app.config import Config
from datetime import datetime, timezone

init_db(Config.DATABASE_PATH)
conn = get_db(Config.DATABASE_PATH)

jobs = scrape_repo('SimplifyJobs', 'Summer2026-Internships', Config.GITHUB_TOKEN)
now = datetime.now(timezone.utc).isoformat()

for job in jobs:
    conn.execute(
        """INSERT OR IGNORE INTO jobs (id, company, role, location, link, repo, notified, seen_at, date_posted)
           VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)""",
        (job['id'], job['company'], job['role'],
         job.get('location',''), job.get('link',''), job['repo'], now,
         job.get('date_posted', ''))
    )

conn.commit()
conn.close()
print(f"Seeded {len(jobs)} jobs as already-notified")