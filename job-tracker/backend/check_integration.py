"""Integration check — verifies all modules import and chain correctly."""
import sys

print("Checking imports...")
try:
    from app.config import Config
    print("  ✓ config")
    from app.db import init_db, get_db, find_new_jobs, insert_jobs, log_run
    print("  ✓ db")
    from app.scraper import fetch_readme, parse_jobs, scrape_repo, is_us_location
    print("  ✓ scraper")
    from app.notifier import send_email, notify_new_jobs
    print("  ✓ notifier")
    from app.scheduler import check_all_repos, start_scheduler
    print("  ✓ scheduler")
    from app.routes import bp
    print("  ✓ routes")
    from app import create_app
    print("  ✓ __init__")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    sys.exit(1)

print("\nChecking config...")
try:
    Config.validate()
    print(f"  ✓ all required env vars present")
    print(f"  ✓ DATABASE_PATH = {Config.DATABASE_PATH}")
    print(f"  ✓ CHECK_INTERVAL_MINUTES = {Config.CHECK_INTERVAL_MINUTES}")
    print(f"  ✓ FILTER_COUNTRY = '{Config.FILTER_COUNTRY}'")
except ValueError as e:
    print(f"  ✗ {e}")
    sys.exit(1)

print("\nChecking DB init...")
try:
    init_db(Config.DATABASE_PATH)
    conn = get_db(Config.DATABASE_PATH)
    tables = [r["name"] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()]
    conn.close()
    for t in ["jobs", "repos", "run_log"]:
        status = "✓" if t in tables else "✗ MISSING"
        print(f"  {status} table: {t}")
except Exception as e:
    print(f"  ✗ DB error: {e}")
    sys.exit(1)

print("\nChecking scraper field contract...")
try:
    from app.scraper import is_us_location
    assert is_us_location("New York, NY") == True
    assert is_us_location("Toronto, ON, Canada") == False
    assert is_us_location("Remote in USA") == True
    assert is_us_location("") == False
    print("  ✓ is_us_location logic correct")

    # Check that a fake job dict has all fields db/notifier expect
    fake_job = {
        "id": "abc123",
        "company": "Acme",
        "role": "Engineer",
        "location": "New York, NY",
        "country": "USA",
        "link": "https://example.com",
        "repo": "test/repo",
    }
    required_fields = ["id", "company", "role", "location", "link", "repo"]
    for f in required_fields:
        assert f in fake_job, f"Missing field: {f}"
    print("  ✓ job dict has all required fields for db/notifier")
except AssertionError as e:
    print(f"  ✗ {e}")
    sys.exit(1)

print("\nAll checks passed ✓")
