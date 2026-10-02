# SitePulse

SitePulse is a Python website quality scanner and REST API that analyzes public
websites for common SEO, accessibility, structural, performance, and link issues.

## Current version: v0.3.0

SitePulse includes:

- single-page scanning
- breadth-first multi-page crawling
- 0–100 page and site health scores
- high / medium / low severity summaries
- heading hierarchy checks
- missing title and meta-description checks
- missing image alt-text checks
- internal and external link discovery
- optional internal broken-link checking
- FastAPI REST API
- API input limits and basic private-network target protection
- automated tests with GitHub Actions

## Tech stack

- Python
- FastAPI
- Pydantic
- Requests
- Beautiful Soup
- Pytest
- HTTPX
- GitHub Actions

## Project structure

```text
sitepulse/
├── src/
│   └── sitepulse/
│       ├── __init__.py
│       ├── api.py
│       ├── cli.py
│       ├── crawler.py
│       ├── linkcheck.py
│       ├── quality.py
│       ├── scanner.py
│       └── security.py
├── tests/
│   ├── test_api.py
│   ├── test_crawler.py
│   ├── test_linkcheck.py
│   ├── test_quality.py
│   ├── test_scanner.py
│   └── test_security.py
├── .github/
│   └── workflows/
│       └── tests.yml
├── pyproject.toml
├── requirements.txt
└── README.md
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

Then open the interactive API documentation at:

```text
http://127.0.0.1:8000/docs
```

Health check:

```http
GET /health
```

Run a website scan:

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

Example response shape:

```json
{
  "start_url": "https://www.python.org",
  "site_health": 98,
  "pages_scanned": 5,
  "total_issues": 3,
  "severity": {
    "high": 0,
    "medium": 0,
    "low": 3
  },
  "pages": [],
  "crawl_errors": [],
  "link_check": {
    "checked": 20,
    "broken_count": 0,
    "broken": []
  }
}
```

## Tests

Run the test suite:

```bash
pytest
```

GitHub Actions also runs the tests automatically for pull requests.

## Roadmap

### v0.1 — Scanner engine ✅
Single-page HTML analysis and CLI reporting.

### v0.2 — Website crawler ✅
Breadth-first internal-link crawling, health scoring, and broken-link checks.

### v0.3 — REST API ✅
Expose SitePulse scans through FastAPI.

### v0.4 — Persistence
Store websites, scans, pages, and issues in SQLite/PostgreSQL.

### v0.5 — Dashboard
Build an interactive HTML/CSS/JavaScript frontend.

### v1.0 — Portfolio release
Docker, deployment, screenshots, polished documentation, and a live demo.

## Why this project exists

SitePulse is a practical software engineering project that combines networking,
HTML parsing, data structures and algorithms, REST APIs, application security,
testing, databases, frontend development, CI/CD, and deployment.
