import csv
from pathlib import Path
from typing import Iterable

from openpyxl import Workbook
from openpyxl.styles import Font

from job_finder.models import Job, RunLog
from job_finder.processing import extract_experience, extract_keywords

JOB_HEADERS = [
    "Source", "Company", "Job Title", "Location", "Experience Required",
    "Salary Min", "Salary Max", "Apply URL", "Posted Date", "Keywords",
]
LOG_HEADERS = ["Timestamp", "Source", "Status", "Jobs Found", "Error"]


def _job_rows(jobs: Iterable[Job]):
    for j in jobs:
        yield [
            j.source, j.company, j.title, j.location,
            extract_experience(j.description),
            j.salary_min, j.salary_max, j.apply_url, j.posted_date,
            ", ".join(extract_keywords(j.description)),
        ]


def write_jobs_csv(path: str, jobs: Iterable[Job]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(JOB_HEADERS)
        writer.writerows(_job_rows(jobs))


def write_jobs_xlsx(path: str, jobs: Iterable[Job]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Jobs"
    worksheet.append(JOB_HEADERS)
    for cell in worksheet[1]:
        cell.font = Font(bold=True)
    for row in _job_rows(jobs):
        worksheet.append(row)
    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions
    workbook.save(path)


def write_jobs(path: str, jobs: Iterable[Job]) -> None:
    suffix = Path(path).suffix.lower()
    if suffix == ".csv":
        write_jobs_csv(path, jobs)
    elif suffix == ".xlsx":
        write_jobs_xlsx(path, jobs)
    else:
        raise ValueError(f"Unsupported output format '{suffix}'. Use .csv or .xlsx.")


def append_run_logs(path: str, logs: Iterable[RunLog]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(LOG_HEADERS)
        for r in logs:
            writer.writerow([r.timestamp, r.source, r.status, r.count, r.error])
