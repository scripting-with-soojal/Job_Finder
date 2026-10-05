import html
import re
from typing import Iterable, List

from job_finder.models import Job

SKILLS = [
    "Python", "SQL", "Snowflake", "Airflow", "Spark", "PySpark", "Databricks",
    "AWS", "Azure", "GCP", "BigQuery", "Redshift", "Kafka", "ETL", "Docker",
    "Kubernetes", "Looker", "Tableau", "Power BI", "dbt",
]

# Most specific patterns first.
_EXPERIENCE_PATTERNS = [
    re.compile(r"(\d+)\s*(?:-|to)\s*(\d+)\s*\+?\s*years?", re.I),
    re.compile(r"(?:minimum|at least)\s*(\d+)\s*years?", re.I),
    re.compile(r"(\d+)\s*\+?\s*years?", re.I),
]


def strip_html(text: str) -> str:
    """Greenhouse returns escaped HTML; convert it to plain text."""
    text = html.unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def deduplicate_jobs(jobs: Iterable[Job]) -> List[Job]:
    seen, unique = set(), []
    for job in jobs:
        if job.dedupe_key in seen:
            continue
        seen.add(job.dedupe_key)
        unique.append(job)
    return unique


def extract_experience(text: str) -> str:
    if not text:
        return "Not Specified"
    for pattern in _EXPERIENCE_PATTERNS:
        m = pattern.search(text)
        if m:
            if m.lastindex == 2:
                return f"{m.group(1)}-{m.group(2)} Years"
            return f"{m.group(1)}+ Years"
    return "Not Specified"


def extract_keywords(text: str) -> List[str]:
    """Skills mentioned in the text, matched on word boundaries."""
    return [
        skill
        for skill in SKILLS
        if re.search(rf"(?<!\w){re.escape(skill)}(?!\w)", text or "", re.I)
    ]
