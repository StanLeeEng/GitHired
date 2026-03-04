import base64
import hashlib
import re
import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta

# All 50 US state abbreviations + DC
US_STATE_ABBREVIATIONS = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC",
}

US_KEYWORDS = {"usa", "u.s.", "u.s.a.", "united states", "remote (us)", "us remote", "remote in usa"}


def is_us_location(location: str) -> bool:
    """Return True if the location string refers to a US location."""
    if not location:
        return False

    location_lower = location.lower().strip()

    for keyword in US_KEYWORDS:
        if keyword in location_lower:
            return True

    # Check each comma-separated segment for a state abbreviation
    parts = [p.strip().upper() for p in location.replace(";", ",").split(",")]
    for part in parts:
        if part in US_STATE_ABBREVIATIONS:
            return True

    return False


def fetch_readme(owner: str, repo: str, token: str) -> str:
    """Fetch the README.md from a GitHub repo.

    Uses the Contents API first; falls back to the raw URL for files
    larger than GitHub's 1 MB contents API limit (encoding == 'none').
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    # Try contents API first
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/README.md"
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    data = response.json()

    if data.get("encoding") == "base64" and data.get("content"):
        return base64.b64decode(data["content"]).decode("utf-8")

    # File too large for contents API — fetch via download_url returned by the API
    download_url = data.get("download_url")
    if not download_url:
        raise ValueError(f"Cannot fetch README for {owner}/{repo}: no content and no download_url")
    raw_response = requests.get(download_url, headers={"Authorization": f"Bearer {token}"}, timeout=30)
    raw_response.raise_for_status()
    return raw_response.text


def _extract_company(td: BeautifulSoup) -> str:
    """Extract company name from a <td>, stripping HTML and emoji."""
    # Try <strong><a>CompanyName</a></strong> pattern first
    a_tag = td.find("a")
    if a_tag:
        name = a_tag.get_text(strip=True)
    else:
        name = td.get_text(strip=True)

    # Strip common emoji prefixes (🔥, 🇺🇸, etc.)
    name = re.sub(r'^[\U00010000-\U0010ffff\U00002600-\U000027BF\U0001F300-\U0001FAFF\s]+', '', name).strip()
    return name


def _extract_location(td: BeautifulSoup) -> str:
    """Extract location text from a <td>, handling <details> and <br> tags."""
    # Replace <br> tags with comma separator before extracting text
    for br in td.find_all("br"):
        br.replace_with(", ")

    # If there's a <details> tag, take the <summary> text as the location label
    details = td.find("details")
    if details:
        summary = details.find("summary")
        if summary:
            return summary.get_text(strip=True)

    return td.get_text(separator=", ", strip=True)


def _extract_link(td: BeautifulSoup) -> str:
    """Extract the application URL from the link <td>."""
    a_tag = td.find("a")
    if a_tag and a_tag.get("href"):
        return a_tag["href"]
    return ""


def _parse_age_to_date(age: str) -> str:
    """Convert an age string like '0d', '3d', '1mo' to an ISO date string."""
    today = date.today()
    age = age.strip().lower()
    try:
        if age.endswith("mo"):
            days = int(age[:-2]) * 30
        elif age.endswith("d"):
            days = int(age[:-1])
        else:
            return today.isoformat()
        return (today - timedelta(days=days)).isoformat()
    except ValueError:
        return today.isoformat()


def parse_jobs(html: str, repo: str) -> list[dict]:
    """Parse HTML tables in the README into a list of job dicts."""
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    last_company = ""

    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            # Skip header rows
            if row.find("th"):
                continue

            cells = row.find_all("td")
            if len(cells) < 3:
                continue

            company_text = cells[0].get_text(strip=True)

            # ↳ means a sub-listing — reuse the last company name
            if company_text == "↳":
                company = last_company
            else:
                company = _extract_company(cells[0])
                if not company:
                    continue
                last_company = company

            role        = cells[1].get_text(strip=True)
            location    = _extract_location(cells[2])
            link        = _extract_link(cells[3]) if len(cells) > 3 else ""
            age_text    = cells[4].get_text(strip=True) if len(cells) > 4 else ""
            date_posted = _parse_age_to_date(age_text) if age_text else date.today().isoformat()

            # Only keep jobs posted today (0d) or yesterday (1d)
            if age_text not in ("0d"):
                continue

            # Skip rows where role is empty or application is closed (🔒)
            if not role or "🔒" in role or "🔒" in link:
                continue

            job_id = hashlib.md5(f"{company}|{role}|{location}".encode()).hexdigest()

            jobs.append({
                "id":          job_id,
                "company":     company,
                "role":        role,
                "location":    location,
                "country":     "USA" if is_us_location(location) else "",
                "link":        link,
                "repo":        repo,
                "date_posted": date_posted,
            })

    return jobs


def scrape_repo(owner: str, repo: str, token: str, country_filter: str = "") -> list[dict]:
    """
    Fetch and parse jobs from a GitHub repo README.
    If country_filter is set (e.g. 'USA'), only return jobs from that country.
    """
    markdown = fetch_readme(owner, repo, token)
    jobs = parse_jobs(markdown, repo=f"{owner}/{repo}")

    if country_filter:
        jobs = [j for j in jobs if j.get("country", "").lower() == country_filter.lower()]

    return jobs
