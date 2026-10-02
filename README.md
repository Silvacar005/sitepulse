# SitePulse

SitePulse is a Python website quality scanner and REST API that analyzes public
websites for common SEO, accessibility, structural, performance, and link issues.

## Current version: v0.4.0

SitePulse now persists scan history in a relational SQLite database.

### Current capabilities

- single-page scanning
- breadth-first multi-page crawling
- 0–100 page and site health scores
- high / medium / low severity summaries
- heading hierarchy checks
- missing title and meta-description checks
- missing image alt-text checks
- internal and external link discovery
- optional internal broken-link checking
- FastAPI REST API with interactive OpenAPI documentation
- relational scan history with SQLAlchemy
- saved pages, issues, crawl errors, and broken links
- API input limits and private-network target protection
- automated tests with GitHub Actions

## Tech stack

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- SQLite
- Requests
- Beautiful Soup
- Pytest
- HTTPX
- GitHub Actions

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

A website can have many scans, which lets SitePulse keep historical results and
eventually show changes in site health over time.

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

Start the development server:

```bash
uvicorn sitepulse.api:app --reload
```

Open the interactive documentation:

```text
http://127.0.0.1:8000/docs
```

### Health check

```http
GET /health
```

### Run and save a scan

```http
POST /api/scans
Content-Type: application/json
```

Example request:

```json
{
  "url": "https://www.python.org",
  "max_pages": 5,
  "check_links": true,
  "max_links": 20
}
```

Every successful scan is saved automatically and receives an integer `id`.

### View scan history

```http
GET /api/scans
```

Optional history limit:

```http
GET /api/scans?limit=10
```

### View one saved scan

```http
GET /api/scans/{scan_id}
```

For example:

```http
GET /api/scans/1
```

## Database

By default SitePulse creates:

```text
sitepulse.db
```

in the project directory.

The database stores websites, scans, pages, issues, crawl errors, and broken
links. Database files are ignored by Git.

The SQLAlchemy connection URL can be overridden with the
`SITEPULSE_DATABASE_URL` environment variable, which prepares the persistence
layer for a production database later.

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

### v0.5 — Dashboard
Build an interactive HTML/CSS/JavaScript frontend with scan history.

### v1.0 — Portfolio release
Docker, production database, deployment, screenshots, polished documentation,
and a live demo.

## Why this project exists

SitePulse is a practical software engineering project that combines networking,
HTML parsing, data structures and algorithms, REST APIs, relational databases,
application security, testing, frontend development, CI/CD, and deployment.
