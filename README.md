# Job Finder

A Python CLI that aggregates job postings from the **Adzuna API** and **Greenhouse** company career boards into one clean, deduplicated CSV or Excel workbook. For each posting it extracts the required years of experience and tags the tech stack mentioned (Python, SQL, Airflow, Snowflake, ...), so you can filter hundreds of listings in seconds.

Originally built as a Google Apps Script + Google Sheets tool; rewritten in Python as a testable, configurable package.

## Features

- **Multi-source ingestion**: paginated Adzuna search plus any number of Greenhouse boards, configured in `config/boards.csv`
- **Deduplication** by apply URL, falling back to `company|title|location`
- **Experience extraction**: regex parsing of phrases like `3-5 years`, `minimum 4 years`, `5+ years`
- **Keyword tagging**: detects 20 data-engineering skills using word boundaries (so `Spark` does not match inside `PySpark`)
- **Fault isolation**: one failing source is logged and skipped, and never aborts the run
- **Resilient HTTP**: automatic retries with backoff on 429 / 5xx responses
- **Run logs**: every source's status, job count and error is appended to `job_run_logs.csv`
- **Secrets from environment**: API keys are never in source control

## Project structure

```
job_finder/
  cli.py          argument parsing, config loading
  pipeline.py     orchestrates sources, isolates failures, dedupes
  sources/
    adzuna.py     paginated Adzuna fetcher
    greenhouse.py Greenhouse board fetcher + title filter
  processing.py   dedupe, experience + keyword extraction, HTML cleanup
  storage.py      CSV/XLSX job writers and CSV run-log writer
  http.py         requests session with retry/backoff
  models.py       Job and RunLog dataclasses
config/boards.csv company boards to scan
tests/            unit + end-to-end tests (mocked HTTP)
```

## Setup

```bash
git clone <your-repo-url> && cd job-finder
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # then add your Adzuna keys
```

Get free Adzuna credentials at https://developer.adzuna.com/.

## Usage

```bash
python -m job_finder --role "data engineer" --country in
python -m job_finder --role "data engineer" --country gb --max-pages 3 --out output/uk.csv
python -m job_finder --role "data engineer" --country in --out output/jobs.xlsx
```

| Option | Description |
|---|---|
| `--role` | Job title to search (also used to filter Greenhouse titles) |
| `--country` | Adzuna country code, e.g. `in`, `gb`, `us` |
| `--boards` | Path to boards CSV (default `config/boards.csv`) |
| `--max-pages` | Max Adzuna pages, 50 jobs each (default 10) |
| `--out` | Job output path ending in `.csv` or `.xlsx` (default `output/jobs.csv`) |
| `--log` | Run-log CSV path (default `output/job_run_logs.csv`) |

**Output columns:** Source, Company, Job Title, Location, Experience Required, Salary Min, Salary Max, Apply URL, Posted Date, Keywords.

To add a company, append a row to `config/boards.csv`. The identifier is the token in the company's Greenhouse URL (`boards.greenhouse.io/<token>`).

## Tests

```bash
python -m unittest discover -v
```

HTTP is mocked, so tests run offline. They cover pagination stopping, failure isolation, missing credentials, inactive boards, HTML cleanup, deduplication, and full CLI runs that check CSV and XLSX output.

## Design notes

- Sources take an injected `session`, so they can be tested without network access.
- Failures are caught per source in the pipeline, not inside the fetchers, so fetchers stay simple and errors are logged in one place.
- Extraction is regex-based by design: fast, deterministic and easy to test. It will miss unusual phrasings.

## Roadmap

- Google Sheets export (`gspread`)
- More sources (Lever, Ashby)
- Scheduled runs (cron / GitHub Actions) with new-job diffing
