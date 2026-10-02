from __future__ import annotations

from dataclasses import asdict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from sitepulse import __version__
from sitepulse.crawler import crawl_site
from sitepulse.linkcheck import check_internal_links
from sitepulse.quality import page_health_score, site_health
from sitepulse.security import validate_public_url


app = FastAPI(
    title="SitePulse API",
    version=__version__,
    description=(
        "Website quality scanning API for SEO, accessibility, "
        "structure, performance, and broken-link checks."
    ),
)


class ScanRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)
    max_pages: int = Field(default=5, ge=1, le=100)
    check_links: bool = False
    max_links: int = Field(default=50, ge=1, le=500)


class SeverityResponse(BaseModel):
    high: int
    medium: int
    low: int


class IssueResponse(BaseModel):
    severity: str
    category: str
    message: str


class PageResponse(BaseModel):
    url: str
    score: int
    status_code: int
    response_time_ms: int
    title: str | None
    h1_count: int
    image_count: int
    images_missing_alt: int
    internal_link_count: int
    external_link_count: int
    issues: list[IssueResponse]


class CrawlErrorResponse(BaseModel):
    url: str
    message: str


class BrokenLinkResponse(BaseModel):
    url: str
    status_code: int | None
    response_time_ms: int
    error: str | None


class LinkCheckResponse(BaseModel):
    checked: int
    broken_count: int
    broken: list[BrokenLinkResponse]


class ScanResponse(BaseModel):
    start_url: str
    site_health: int
    pages_scanned: int
    total_issues: int
    severity: SeverityResponse
    pages: list[PageResponse]
    crawl_errors: list[CrawlErrorResponse]
    link_check: LinkCheckResponse | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.post("/api/scans", response_model=ScanResponse)
def create_scan(request: ScanRequest) -> ScanResponse:
    try:
        safe_url = validate_public_url(request.url)
        crawl = crawl_site(safe_url, max_pages=request.max_pages)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not crawl.pages:
        detail = "SitePulse could not scan any pages."
        if crawl.errors:
            detail = f"{detail} {crawl.errors[0].message}"
        raise HTTPException(status_code=502, detail=detail)

    health_result = site_health(crawl.pages)

    pages = [
        PageResponse(
            url=page.url,
            score=page_health_score(page),
            status_code=page.status_code,
            response_time_ms=page.response_time_ms,
            title=page.title,
            h1_count=page.h1_count,
            image_count=page.image_count,
            images_missing_alt=page.images_missing_alt,
            internal_link_count=len(page.internal_links),
            external_link_count=len(page.external_links),
            issues=[IssueResponse(**asdict(issue)) for issue in page.issues],
        )
        for page in crawl.pages
    ]

    link_response = None

    if request.check_links:
        link_summary = check_internal_links(
            crawl.pages,
            max_links=request.max_links,
        )
        link_response = LinkCheckResponse(
            checked=link_summary.checked,
            broken_count=len(link_summary.broken),
            broken=[
                BrokenLinkResponse(
                    url=item.url,
                    status_code=item.status_code,
                    response_time_ms=item.response_time_ms,
                    error=item.error,
                )
                for item in link_summary.broken
            ],
        )

    return ScanResponse(
        start_url=crawl.start_url,
        site_health=health_result.score,
        pages_scanned=crawl.pages_scanned,
        total_issues=crawl.total_issues,
        severity=SeverityResponse(
            high=health_result.severity.high,
            medium=health_result.severity.medium,
            low=health_result.severity.low,
        ),
        pages=pages,
        crawl_errors=[
            CrawlErrorResponse(url=item.url, message=item.message)
            for item in crawl.errors
        ],
        link_check=link_response,
    )
