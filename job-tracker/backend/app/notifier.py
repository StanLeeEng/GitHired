import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone
import sqlite3


def _build_digest(jobs: list[dict]) -> tuple[str, str]:
    """Return (subject, html_body) for a digest of all jobs."""
    count = len(jobs)
    subject = f"GitHired: {count} new internship{'s' if count != 1 else ''} found"

    rows_html = ""
    rows_plain = ""
    for j in jobs:
        link = j.get("link", "")
        apply_html = f'<a href="{link}" style="color:#6366f1;">Apply</a>' if link else "—"
        apply_plain = link if link else "—"
        rows_html += f"""
        <tr>
          <td style="padding:8px 12px;border-bottom:1px solid #27272a;font-weight:600;color:#f4f4f5;">{j['company']}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #27272a;color:#d4d4d8;">{j['role']}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #27272a;color:#a1a1aa;">{j.get('location','')}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #27272a;">{apply_html}</td>
        </tr>"""
        rows_plain += f"  {j['company']} | {j['role']} | {j.get('location','')} | {apply_plain}\n"

    html = f"""<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#09090b;font-family:sans-serif;">
  <div style="max-width:700px;margin:32px auto;background:#18181b;border-radius:8px;border:1px solid #27272a;overflow:hidden;">
    <div style="padding:20px 24px;border-bottom:1px solid #27272a;">
      <h1 style="margin:0;font-size:18px;color:#f4f4f5;">
        GitHired &mdash; {count} new internship{'s' if count != 1 else ''}
      </h1>
      <p style="margin:4px 0 0;font-size:13px;color:#71717a;">
        {datetime.now().strftime('%B %d, %Y')}
      </p>
    </div>
    <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;font-size:14px;">
      <thead>
        <tr style="background:#09090b;">
          <th style="padding:8px 12px;text-align:left;color:#71717a;font-weight:500;">Company</th>
          <th style="padding:8px 12px;text-align:left;color:#71717a;font-weight:500;">Role</th>
          <th style="padding:8px 12px;text-align:left;color:#71717a;font-weight:500;">Location</th>
          <th style="padding:8px 12px;text-align:left;color:#71717a;font-weight:500;">Link</th>
        </tr>
      </thead>
      <tbody>{rows_html}
      </tbody>
    </table>
  </div>
</body>
</html>"""

    plain = f"GitHired — {count} new internship{'s' if count != 1 else ''}\n{datetime.now().strftime('%B %d, %Y')}\n\n{rows_plain}"
    return subject, html, plain


def send_digest(jobs: list[dict], sender: str, password: str, recipient: str) -> bool:
    """Send a single digest email for all new jobs."""
    if not jobs:
        return True

    subject, html, plain = _build_digest(jobs)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender, password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        return False


def notify_new_jobs(jobs: list[dict], conn: sqlite3.Connection, sender: str, password: str, recipient: str):
    """Send a single digest email for all new jobs and mark them as notified."""
    if not jobs:
        return

    success = send_digest(jobs, sender, password, recipient)
    if success:
        now = datetime.now(timezone.utc).isoformat()
        for job in jobs:
            conn.execute(
                "UPDATE jobs SET notified = 1, notified_at = ? WHERE id = ?",
                (now, job["id"]),
            )
        conn.commit()
