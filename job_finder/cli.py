import argparse
import csv
import logging
import os

from job_finder import __version__
from job_finder.pipeline import run_pipeline
from job_finder.storage import append_run_logs, write_jobs

try:  # optional: load keys from a local .env file
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass


def load_boards(path: str) -> list:
    """Read the company boards config (company,type,identifier,active)."""
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return [
            {
                "company": row["company"].strip(),
                "type": row["type"].strip().lower(),
                "identifier": row["identifier"].strip(),
                "active": row["active"].strip().lower() == "true",
            }
            for row in csv.DictReader(f)
        ]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="job_finder",
        description="Aggregate job postings from Adzuna and Greenhouse boards.",
    )
    p.add_argument("--role", required=True, help='Job title to search, e.g. "data engineer"')
    p.add_argument("--country", required=True, help="Adzuna country code, e.g. in, gb, us")
    p.add_argument("--boards", default="config/boards.csv", help="Company boards CSV")
    p.add_argument("--max-pages", type=int, default=10, help="Max Adzuna pages (50 jobs each)")
    p.add_argument("--out", default="output/jobs.csv")
    p.add_argument("--log", default="output/job_run_logs.csv")
    p.add_argument("--version", action="version", version=__version__)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    jobs, logs = run_pipeline(
        role=args.role,
        country=args.country,
        boards=load_boards(args.boards),
        adzuna_id=os.environ.get("ADZUNA_APP_ID"),
        adzuna_key=os.environ.get("ADZUNA_APP_KEY"),
        max_pages=args.max_pages,
    )
    write_jobs(args.out, jobs)
    append_run_logs(args.log, logs)

    for r in logs:
        print(f"{r.source:<14} {r.status:<8} {r.count:>4} {r.error}")
    print(f"\nCompleted. {len(jobs)} unique jobs -> {args.out}")
    return 0
