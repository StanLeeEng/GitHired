from apscheduler.schedulers.background import BackgroundScheduler
from app.scraper import scrape_repo
from app.db import get_db, find_new_jobs, insert_jobs, log_run
from app.notifier import notify_new_jobs
from app.config import Config


def check_all_repos(app):
    """
    Scrapes all active repos in the database, finds new jobs,
    saves them, and sends email notifications.
    Runs inside the Flask app context so it can access config.
    """
    with app.app_context():
        conn = get_db(Config.DATABASE_PATH)

        # Get all active repos from the repos table
        repos = conn.execute(
            "SELECT owner, name FROM repos WHERE active = 1"
        ).fetchall()

        for repo_row in repos:
            owner = repo_row["owner"]
            name  = repo_row["name"]
            repo_str = f"{owner}/{name}"

            try:
                # 1. Scrape jobs from GitHub (with optional US filter)
                jobs = scrape_repo(
                    owner=owner,
                    repo=name,
                    token=Config.GITHUB_TOKEN,
                    country_filter=Config.FILTER_COUNTRY,
                )

                # 2. Find only jobs not already in the database
                new_jobs = find_new_jobs(jobs, conn)

                # 3. Save new jobs to the database
                insert_jobs(new_jobs, conn)

                # 4. Send email notifications for each new job
                notify_new_jobs(
                    jobs=new_jobs,
                    conn=conn,
                    sender=Config.EMAIL_SENDER,
                    password=Config.EMAIL_PASSWORD,
                    recipient=Config.EMAIL_RECIPIENT,
                )

                # 5. Log the run as successful
                log_run(
                    repo=repo_str,
                    jobs_found=len(jobs),
                    jobs_new=len(new_jobs),
                    status="success",
                    conn=conn,
                )

                print(f"[scheduler] {repo_str}: {len(jobs)} found, {len(new_jobs)} new")

            except Exception as e:
                # Log the error but keep the scheduler running
                log_run(
                    repo=repo_str,
                    jobs_found=0,
                    jobs_new=0,
                    status="error",
                    conn=conn,
                    error_msg=str(e),
                )
                print(f"[scheduler] ERROR on {repo_str}: {e}")

        conn.close()


def start_scheduler(app):
    """
    Creates and starts the APScheduler background scheduler.
    Attaches it to the Flask app so it can be shut down cleanly.
    """
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        func=lambda: check_all_repos(app),
        trigger="interval",
        minutes=Config.CHECK_INTERVAL_MINUTES,
        id="job_check",
        replace_existing=True,
    )

    scheduler.start()
    print(f"[scheduler] Started — checking every {Config.CHECK_INTERVAL_MINUTES} minutes")
    return scheduler
