# SitePulse

[![CI](https://github.com/Silvacar005/sitepulse/actions/workflows/tests.yml/badge.svg)](https://github.com/Silvacar005/sitepulse/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)
![FastAPI](https://img.shields.io/badge/FastAPI-REST%20API-009688)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-production-4169E1)

**SitePulse** is a full-stack website quality scanner built by **Carlos Silva**.
It crawls public websites, identifies SEO, accessibility, structure, performance,
and link-health issues, calculates a 0–100 health score, and stores scan history
for later review.

## Highlights

- responsive HTML/CSS/JavaScript dashboard
- breadth-first multi-page crawler
- 0–100 site and page health scoring
- high / medium / low severity classification
- title and meta-description checks
- heading hierarchy analysis
- image alt-text checks
- internal and external link discovery
- optional broken-link checking
- FastAPI REST API with OpenAPI documentation
- SQLAlchemy relational persistence
- SQLite for local development
- PostgreSQL support for production
- SSRF-oriented public-target validation
- Docker and Docker Compose support
- Render deployment Blueprint
- automated tests and Docker builds with GitHub Actions

## Dashboard

The dashboard lets a user enter a website, choose a crawl limit, optionally check
links, inspect health metrics, expand page-level findings, and reopen previous
scans from persistent history.

Example result from scanning Python.org:

```text
Site health     98 / 100
Pages scanned    5
Total issues     3
Broken links     0

Severity
High             0
Medium           0
Low              3
```

## Architecture

```mermaid
flowchart TD
    Browser[Browser Dashboard] --> API[FastAPI REST API]
    CLI[CLI] --> Crawler
    API --> Crawler[Website Crawler]
    Crawler --> Scanner[HTML Scanner]
    Crawler --> Links[Link Checker]
    Scanner --> Quality[Health Scoring]
    API --> Persistence[Persistence Layer]
    Persistence --> ORM[SQLAlchemy]
    ORM --> SQLite[(SQLite - Local)]
    ORM --> Postgres[(PostgreSQL - Production)]
```

## Data model

```mermaid
erDiagram
    WEBSITE ||--o{ SCAN : has
    SCAN ||--o{ PAGE : contains
    PAGE ||--o{ ISSUE : reports
    SCAN ||--o{ CRAWL_ERROR : records
    SCAN ||--o{ BROKEN_LINK : records
```

## Tech stack

**Backend:** Python, FastAPI, Pydantic, Requests, Beautiful Soup  
**Data:** SQLAlchemy, SQLite, PostgreSQL, psycopg  
**Frontend:** HTML, CSS, JavaScript  
**Quality:** Pytest, HTTPX, GitHub Actions  
**Deployment:** Docker, Docker Compose, Render

## Quick start

Clone the repository:

```bash
git clone https://github.com/Silvacar005/sitepulse.git
cd sitepulse
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Install the project:

```bash
pip install -e .
```

Start SitePulse:

```bash
uvicorn sitepulse.api:app --reload
```

Open:

```text
Dashboard: http://127.0.0.1:8000/
API docs:  http://127.0.0.1:8000/docs
```

## Docker

Run SitePulse alone with SQLite:

```bash
docker build -t sitepulse .
docker run --rm -p 8000:8000 sitepulse
```

Run the complete local production-style stack with PostgreSQL:

```bash
docker compose up --build
```

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for deployment details.

## REST API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Service health and version |
| `POST` | `/api/scans` | Run and persist a scan |
| `GET` | `/api/scans` | List recent scan history |
| `GET` | `/api/scans/{scan_id}` | Retrieve a saved scan |

Example request:

```json
{
  "url": "https://www.python.org",
  "max_pages": 5,
  "check_links": true,
  "max_links": 20
}
```

## CLI

Scan one page:

```bash
sitepulse https://example.com
```

Crawl multiple pages:

```bash
sitepulse https://www.python.org --crawl --max-pages 5
```

Crawl and check internal links:

```bash
sitepulse https://www.python.org --crawl --max-pages 5 --check-links --max-links 20
```

## Database configuration

SitePulse uses SQLite by default:

```text
sqlite:///./sitepulse.db
```

For production, set:

```text
SITEPULSE_DATABASE_URL=postgresql://user:password@host:5432/database
```

Standard Render-style `postgresql://` connection strings are normalized for
the psycopg 3 SQLAlchemy driver automatically.

## Tests

Run:

```bash
pytest
```

Every pull request runs the full test suite and builds the production Docker
image through GitHub Actions.

## Project evolution

| Version | Milestone |
| --- | --- |
| v0.1 | Single-page scanner and CLI |
| v0.2 | BFS crawler, scoring, and link checks |
| v0.3 | FastAPI REST API |
| v0.4 | Relational scan persistence |
| v0.5 | Interactive dashboard |
| **v1.0** | **Docker, PostgreSQL, CI, and cloud deployment readiness** |

## Security

SitePulse only intends to scan public HTTP/HTTPS websites. The API rejects
obvious localhost, private, link-local, and other non-public network targets.

See [SECURITY.md](SECURITY.md) for additional details.

## Copyright and authorship

Copyright © 2026 Carlos Silva. All rights reserved.

This repository is publicly available for portfolio and educational review. No
license is granted to copy, redistribute, sublicense, modify, or use this
software in another project except as permitted by applicable law or GitHub's
Terms of Service.

See [COPYRIGHT.md](COPYRIGHT.md) for the full notice.
