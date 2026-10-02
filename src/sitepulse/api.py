from __future__ import annotations

from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from sitepulse import __version__
from sitepulse.crawler import crawl_site
from sitepulse.database import ScanRecord, get_db, init_db
from sitepulse.linkcheck import check_internal_links
from sitepulse.persistence import get_scan, list_scans, save_scan
from sitepulse.security import validate_public_url


init_db()

app = FastAPI(
    title="SitePulse API",
    version=__version__,
    description=(
        "Website quality scanning API for SEO, accessibility, "
        "structure, performance, broken-link checks, and scan history."
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
    meta_description: str | None
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
    id: int
    created_at: datetime
    start_url: str
    site_health: int
    pages_scanned: int
    total_issues: int
    severity: SeverityResponse
    pages: list[PageResponse]
    crawl_errors: list[CrawlErrorResponse]
    link_check: LinkCheckResponse | None = None


class ScanHistoryItem(BaseModel):
    id: int
    created_at: datetime
    start_url: str
    site_health: int
    pages_scanned: int
    total_issues: int
    severity: SeverityResponse
    links_checked: int
    broken_links_count: int


class ScanHistoryResponse(BaseModel):
    scans: list[ScanHistoryItem]


def scan_record_to_response(scan: ScanRecord) -> ScanResponse:
    link_check = None

    if scan.link_check_enabled:
        link_check = LinkCheckResponse(
            checked=scan.links_checked,
            broken_count=scan.broken_links_count,
            broken=[
                BrokenLinkResponse(
                    url=item.url,
                    status_code=item.status_code,
                    response_time_ms=item.response_time_ms,
                    error=item.error,
                )
                for item in scan.broken_links
            ],
        )

    return ScanResponse(
        id=scan.id,
        created_at=scan.created_at,
        start_url=scan.website.url,
        site_health=scan.site_health,
        pages_scanned=scan.pages_scanned,
        total_issues=scan.total_issues,
        severity=SeverityResponse(
            high=scan.high_issues,
            medium=scan.medium_issues,
            low=scan.low_issues,
        ),
        pages=[
            PageResponse(
                url=page.url,
                score=page.score,
                status_code=page.status_code,
                response_time_ms=page.response_time_ms,
                title=page.title,
                meta_description=page.meta_description,
                h1_count=page.h1_count,
                image_count=page.image_count,
                images_missing_alt=page.images_missing_alt,
                internal_link_count=page.internal_link_count,
                external_link_count=page.external_link_count,
                issues=[
                    IssueResponse(
                        severity=issue.severity,
                        category=issue.category,
                        message=issue.message,
                    )
                    for issue in page.issues
                ],
            )
            for page in scan.pages
        ],
        crawl_errors=[
            CrawlErrorResponse(url=item.url, message=item.message)
            for item in scan.crawl_errors
        ],
        link_check=link_check,
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.post("/api/scans", response_model=ScanResponse)
def create_scan(
    request: ScanRequest,
    db: Session = Depends(get_db),
) -> ScanResponse:
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

    link_summary = None

    if request.check_links:
        link_summary = check_internal_links(
            crawl.pages,
            max_links=request.max_links,
        )

    saved = save_scan(db, crawl, link_summary=link_summary)
    return scan_record_to_response(saved)


@app.get("/api/scans", response_model=ScanHistoryResponse)
def get_scan_history(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ScanHistoryResponse:
    records = list_scans(db, limit=limit)

    return ScanHistoryResponse(
        scans=[
            ScanHistoryItem(
                id=scan.id,
                created_at=scan.created_at,
                start_url=scan.website.url,
                site_health=scan.site_health,
                pages_scanned=scan.pages_scanned,
                total_issues=scan.total_issues,
                severity=SeverityResponse(
                    high=scan.high_issues,
                    medium=scan.medium_issues,
                    low=scan.low_issues,
                ),
                links_checked=scan.links_checked,
                broken_links_count=scan.broken_links_count,
            )
            for scan in records
        ]
    )


@app.get("/api/scans/{scan_id}", response_model=ScanResponse)
def get_saved_scan(
    scan_id: int,
    db: Session = Depends(get_db),
) -> ScanResponse:
    saved = get_scan(db, scan_id)

    if saved is None:
        raise HTTPException(status_code=404, detail="Scan not found.")

    return scan_record_to_response(saved)
