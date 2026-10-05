from typing import List

from job_finder.http import DEFAULT_TIMEOUT
from job_finder.models import Job
from job_finder.processing import strip_html

BASE_URL = "https://boards-api.greenhouse.io/v1/boards"


def fetch_jobs(session, company: str, token: str, role: str) -> List[Job]:
    """Fetch a company's Greenhouse board and keep titles matching the role."""
    resp = session.get(
        f"{BASE_URL}/{token}/jobs",
        params={"content": "true"},
        timeout=DEFAULT_TIMEOUT,
    )
    resp.raise_for_status()

    jobs: List[Job] = []
    for j in resp.json().get("jobs", []):
        title = j.get("title", "")
        if role.lower() not in title.lower():
            continue
        jobs.append(
            Job(
                source="Greenhouse",
                company=company,
                title=title,
                location=(j.get("location") or {}).get("name", ""),
                description=strip_html(j.get("content", "")),
                apply_url=j.get("absolute_url", ""),
                posted_date=j.get("updated_at", ""),
            )
        )
    return jobs
