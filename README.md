# SitePulse

SitePulse is a full-stack website quality scanner that analyzes public websites
for common SEO, accessibility, structural, performance, and link issues.

## Current version: v0.5.0

SitePulse now includes a responsive web dashboard on top of the existing REST API
and relational scan history.

### Current capabilities

- responsive HTML/CSS/JavaScript dashboard
- scan form with configurable crawl and link-check limits
- 0–100 site health visualization
- high / medium / low severity summaries
- expandable page-level analysis
- clickable persistent scan history
- single-page and breadth-first multi-page scanning
- heading hierarchy, metadata, and image alt-text checks
- internal/external link discovery and optional broken-link checks
- FastAPI REST API with interactive OpenAPI documentation
- SQLAlchemy + SQLite relational persistence
- private-network target protection
- automated tests with GitHub Actions

## Tech stack

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- SQLite
- HTML
- CSS
- JavaScript
- Requests
- Beautiful Soup
- Pytest
- HTTPX
- GitHub Actions

## Architecture

```text
Browser Dashboard
       │
       ▼
FastAPI REST API
       │
       ├── Scanner / Crawler
       │       ├── SEO checks
       │       ├── Accessibility checks
       │       ├── Structure checks
       │       └── Link checks
       │
       ▼
SQLAlchemy
       │
       ▼
SQLite
```

## Data model

```text
Website
   │
   └── Scan
        ├── Page
        │    └── Issue
        ├── Crawl Error
        └── Broken Link
```

## Setup

Clone the repository and enter the project directory:

```bash
git clone https://github.com/Silvacar005/sitepulse.git
cd sitepulse
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Install SitePulse:

```bash
pip install -e .
```

## Run the web application

Start the development server:

```bash
uvicorn sitepulse.api:app --reload
```

Open the dashboard:

```text
http://127.0.0.1:8000/
```

Open the interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

The dashboard uses the same REST API as external clients. Running a scan from the
browser automatically persists it to the database and refreshes the recent-scan
history.

## Command-line usage

Scan one page:

```bash
sitepulse https://example.com
```

Crawl multiple pages:

```bash
sitepulse https://www.python.org --crawl --max-pages 5
```

Crawl and check discovered internal links:

```bash
sitepulse https://www.python.org --crawl --max-pages 5 --check-links --max-links 20
```

## REST API

```text
GET  /health
POST /api/scans
GET  /api/scans
GET  /api/scans/{scan_id}
```

Example scan request:

```json
{
  "url": "https://www.python.org",
  "max_pages": 5,
  "check_links": true,
  "max_links": 20
}
```

## Database

By default SitePulse creates `sitepulse.db` in the project directory. Database
files are ignored by Git.

The SQLAlchemy connection URL can be overridden with the
`SITEPULSE_DATABASE_URL` environment variable.

## Tests

Run the full test suite:

```bash
pytest
```

GitHub Actions automatically runs the tests for pull requests.

## Roadmap

### v0.1 — Scanner engine ✅
Single-page HTML analysis and CLI reporting.

### v0.2 — Website crawler ✅
Breadth-first crawling, health scoring, and broken-link checks.

### v0.3 — REST API ✅
Expose SitePulse scans through FastAPI.

### v0.4 — Persistence ✅
Store websites, scans, pages, issues, crawl errors, and broken links with
SQLAlchemy and SQLite.

### v0.5 — Dashboard ✅
Responsive HTML/CSS/JavaScript frontend with scan results and persistent history.

### v1.0 — Portfolio release
Docker, PostgreSQL, cloud deployment, screenshots, polished documentation, and
a live public demo.

## Why this project exists

SitePulse is a practical software engineering project that combines networking,
HTML parsing, data structures and algorithms, REST APIs, relational databases,
application security, testing, frontend development, CI/CD, and deployment.

## Copyright and authorship

Copyright © 2026 Carlos Silva. All rights reserved.

SitePulse is publicly available for portfolio and educational review. No license
is granted to copy, redistribute, sublicense, modify, or use this software in
another project except as permitted by applicable law or GitHub's Terms of
Service.

See [COPYRIGHT.md](COPYRIGHT.md) for the full notice.
