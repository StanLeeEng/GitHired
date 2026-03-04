from flask import Blueprint, jsonify, request
from datetime import datetime, timezone, timedelta
from app.db import get_db
from app.config import Config

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/health")
def health():
    """Returns app status, total jobs tracked, and last run info."""
    conn = get_db(Config.DATABASE_PATH)

    jobs_total = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    last_run = conn.execute(
        "SELECT ran_at, status FROM run_log ORDER BY ran_at DESC LIMIT 1"
    ).fetchone()

    conn.close()
    return jsonify({
        "status": "ok",
        "jobs_total": jobs_total,
        "last_run": dict(last_run) if last_run else None,
    })


@bp.route("/jobs")
def get_jobs():
    """
    Returns a paginated list of all jobs.
    Optional query params: ?company=&role=&location=&page=&per_page=
    """
    company      = request.args.get("company", "").strip()
    role         = request.args.get("role", "").strip()
    location     = request.args.get("location", "").strip()
    date_posted  = request.args.get("date_posted", "").strip()   # exact YYYY-MM-DD
    posted_after = request.args.get("posted_after", "").strip()  # YYYY-MM-DD (>=)
    page     = max(1, int(request.args.get("page", 1)))
    per_page = min(100, int(request.args.get("per_page", 25)))
    offset   = (page - 1) * per_page

    query  = "SELECT * FROM jobs WHERE 1=1"
    params = []

    if company:
        query += " AND company LIKE ?"
        params.append(f"%{company}%")
    if role:
        query += " AND role LIKE ?"
        params.append(f"%{role}%")
    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")
    if date_posted:
        query += " AND date_posted = ?"
        params.append(date_posted)
    if posted_after:
        query += " AND date_posted >= ?"
        params.append(posted_after)

    min_hours = request.args.get("min_hours", type=float)
    max_hours = request.args.get("max_hours", type=float)
    now = datetime.now(timezone.utc)
    if max_hours is not None:
        query += " AND seen_at >= ?"
        params.append((now - timedelta(hours=max_hours)).isoformat())
    if min_hours is not None:
        query += " AND seen_at <= ?"
        params.append((now - timedelta(hours=min_hours)).isoformat())

    query += " ORDER BY date_posted DESC, seen_at DESC LIMIT ? OFFSET ?"
    params.extend([per_page, offset])

    count_query = "SELECT COUNT(*) FROM jobs WHERE 1=1"
    count_params: list = []
    if company:
        count_query += " AND company LIKE ?"
        count_params.append(f"%{company}%")
    if role:
        count_query += " AND role LIKE ?"
        count_params.append(f"%{role}%")
    if location:
        count_query += " AND location LIKE ?"
        count_params.append(f"%{location}%")
    if date_posted:
        count_query += " AND date_posted = ?"
        count_params.append(date_posted)
    if posted_after:
        count_query += " AND date_posted >= ?"
        count_params.append(posted_after)
    if max_hours is not None:
        count_query += " AND seen_at >= ?"
        count_params.append((now - timedelta(hours=max_hours)).isoformat())
    if min_hours is not None:
        count_query += " AND seen_at <= ?"
        count_params.append((now - timedelta(hours=min_hours)).isoformat())

    conn = get_db(Config.DATABASE_PATH)
    rows = conn.execute(query, params).fetchall()
    total = conn.execute(count_query, count_params).fetchone()[0]
    conn.close()

    return jsonify({
        "jobs": [dict(r) for r in rows],
        "page": page,
        "per_page": per_page,
        "total": total,
    })


@bp.route("/jobs/new")
def get_new_jobs():
    """Returns jobs seen within a time window. Defaults to last 24 hours.
    Optional query params: ?min_hours=24&max_hours=48
    """
    min_hours = request.args.get("min_hours", 0, type=float)
    max_hours = request.args.get("max_hours", 24, type=float)
    now = datetime.now(timezone.utc)
    since = (now - timedelta(hours=max_hours)).isoformat()
    until = (now - timedelta(hours=min_hours)).isoformat()

    conn = get_db(Config.DATABASE_PATH)
    rows = conn.execute(
        "SELECT * FROM jobs WHERE seen_at >= ? AND seen_at <= ? ORDER BY seen_at DESC",
        (since, until)
    ).fetchall()
    conn.close()

    return jsonify([dict(r) for r in rows])


@bp.route("/repos")
def get_repos():
    """Returns all monitored repositories."""
    conn = get_db(Config.DATABASE_PATH)
    rows = conn.execute("SELECT * FROM repos ORDER BY added_at DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@bp.route("/repos", methods=["POST"])
def add_repo():
    """
    Adds a new repo to monitor.
    Body: { "owner": "SimplifyJobs", "name": "New-Grad-Positions" }
    """
    data = request.get_json()
    owner = (data or {}).get("owner", "").strip()
    name  = (data or {}).get("name", "").strip()

    if not owner or not name:
        return jsonify({"error": "owner and name are required"}), 400

    conn = get_db(Config.DATABASE_PATH)
    conn.execute(
        "INSERT INTO repos (owner, name, added_at) VALUES (?, ?, ?)",
        (owner, name, datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    conn.close()

    return jsonify({"message": f"Added {owner}/{name}"}), 201


@bp.route("/run", methods=["POST"])
def manual_run():
    """Manually triggers a scrape run outside of the scheduler interval."""
    from app.scheduler import check_all_repos
    from flask import current_app

    try:
        check_all_repos(current_app._get_current_object())
        return jsonify({"message": "Run complete"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/jobs", methods=["DELETE"])
def clear_jobs():
    """Deletes all jobs from the database."""
    conn = get_db(Config.DATABASE_PATH)
    deleted = conn.execute("DELETE FROM jobs").rowcount
    conn.commit()
    conn.close()
    return jsonify({"message": f"Deleted {deleted} jobs"})


@bp.route("/runs")
def get_runs():
    """Returns the last 20 scheduler run log entries."""
    conn = get_db(Config.DATABASE_PATH)
    rows = conn.execute(
        "SELECT * FROM run_log ORDER BY ran_at DESC LIMIT 20"
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])
