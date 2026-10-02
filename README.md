# SitePulse

SitePulse is a website quality scanner that checks webpages for common SEO,
accessibility, and structural issues.

The long-term goal is to turn the scanner into a full-stack dashboard that can
crawl websites, store scan history, visualize site health, and expose results
through a REST API.

## Current version: v0.2

SitePulse now includes a Python scanning engine, command-line interface, and breadth-first multi-page crawler.

### Checks currently implemented

- HTTP status code
- Response time
- Missing page title
- Missing meta description
- Missing or multiple H1 headings
- Images missing alt text
- Internal link extraction
- External link extraction

## Tech stack

- Python
- Requests
- Beautiful Soup
- Pytest

Planned additions:

- FastAPI REST API
- SQLite / PostgreSQL
- Multi-page website crawler
- Broken-link detection
- HTML/CSS/JavaScript dashboard
- Authentication
- Docker
- GitHub Actions
- Cloud deployment

## Project structure

```text
sitepulse/
├── src/
│   └── sitepulse/
│       ├── __init__.py
│       ├── cli.py
│       └── scanner.py
├── tests/
│   └── test_scanner.py
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Setup

Clone the repository and create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install SitePulse in editable mode:

```bash
pip install -e .
```

Install the test runner:

```bash
pip install pytest
```

## Run a scan

```bash
sitepulse https://example.com
```

You can also enter a domain without the protocol:

```bash
sitepulse example.com
```

## Run tests

```bash
pytest
```

## Roadmap

### v0.1 — Scanner engine
Single-page HTML analysis and CLI reporting.

### v0.2 — Website crawler
Follow internal links, avoid duplicate visits, and scan multiple pages.

### v0.3 — REST API
Expose scans through FastAPI.

### v0.4 — Persistence
Store websites, scans, and issues in a database.

### v0.5 — Dashboard
Build an interactive HTML/CSS/JavaScript frontend.

### v1.0 — Production portfolio release
Testing, CI/CD, Docker, deployment, screenshots, documentation, and live demo.

## Why this project exists

SitePulse is being built as a practical software engineering project that
combines networking, HTML parsing, algorithms, APIs, databases, frontend
development, testing, and deployment in one application.
