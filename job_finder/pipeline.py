import logging
from datetime import datetime
from typing import List, Optional, Sequence, Tuple

from job_finder.http import build_session
from job_finder.models import Job, RunLog
from job_finder.processing import deduplicate_jobs
from job_finder.sources import adzuna, greenhouse

log = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def run_pipeline(
    role: str,
    country: str,
    boards: Sequence[dict],
    adzuna_id: Optional[str] = None,
    adzuna_key: Optional[str] = None,
    max_pages: int = 10,
    session=None,
) -> Tuple[List[Job], List[RunLog]]:
    """Fetch from every source, isolating failures so one bad source
    never stops the run. Returns (deduplicated jobs, run logs)."""
    session = session or build_session()
    jobs: List[Job] = []
    logs: List[RunLog] = []

    try:
        if not (adzuna_id and adzuna_key):
            raise RuntimeError("ADZUNA_APP_ID / ADZUNA_APP_KEY not set")
        found = adzuna.fetch_jobs(
            session, role, country, adzuna_id, adzuna_key, max_pages=max_pages
        )
        jobs.extend(found)
        logs.append(RunLog(_now(), "Adzuna", "SUCCESS", len(found)))
    except Exception as exc:  # noqa: BLE001 - logged and reported per source
        log.warning("Adzuna failed: %s", exc)
        logs.append(RunLog(_now(), "Adzuna", "FAILED", 0, str(exc)))

    for board in boards:
        if not board["active"] or board["type"] != "greenhouse":
            continue
        try:
            found = greenhouse.fetch_jobs(
                session, board["company"], board["identifier"], role
            )
            jobs.extend(found)
            logs.append(RunLog(_now(), board["company"], "SUCCESS", len(found)))
        except Exception as exc:  # noqa: BLE001
            log.warning("%s failed: %s", board["company"], exc)
            logs.append(RunLog(_now(), board["company"], "FAILED", 0, str(exc)))

    return deduplicate_jobs(jobs), logs
