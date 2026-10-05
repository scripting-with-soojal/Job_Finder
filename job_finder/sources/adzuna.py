import time
from typing import List

from job_finder.http import DEFAULT_TIMEOUT
from job_finder.models import Job

BASE_URL = "https://api.adzuna.com/v1/api/jobs"


def fetch_jobs(
    session,
    role: str,
    country: str,
    app_id: str,
    app_key: str,
    max_pages: int = 10,
    delay: float = 0.5,
    results_per_page: int = 50,
) -> List[Job]:
    """Fetch postings page by page until Adzuna returns no more results."""
    jobs: List[Job] = []
    for page in range(1, max_pages + 1):
        resp = session.get(
            f"{BASE_URL}/{country}/search/{page}",
            params={
                "app_id": app_id,
                "app_key": app_key,
                "results_per_page": results_per_page,
                "what": role,
            },
            timeout=DEFAULT_TIMEOUT,
        )
        resp.raise_for_status()
        results = resp.json().get("results") or []
        if not results:
            break

        for j in results:
            jobs.append(
                Job(
                    source="Adzuna",
                    company=(j.get("company") or {}).get("display_name", ""),
                    title=j.get("title", ""),
                    location=(j.get("location") or {}).get("display_name", ""),
                    description=j.get("description", ""),
                    apply_url=j.get("redirect_url", ""),
                    salary_min=j.get("salary_min") or "",
                    salary_max=j.get("salary_max") or "",
                    posted_date=j.get("created", ""),
                )
            )
        if delay:
            time.sleep(delay)
    return jobs
