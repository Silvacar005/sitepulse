from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session, selectinload

from sitepulse.crawler import CrawlResult
from sitepulse.database import (
    BrokenLinkRecord,
    CrawlErrorRecord,
    IssueRecord,
    PageRecord,
    ScanRecord,
    Website,
)
from sitepulse.linkcheck import LinkCheckSummary
from sitepulse.quality import page_health_score, site_health


def save_scan(
    db: Session,
    crawl: CrawlResult,
    link_summary: LinkCheckSummary | None = None,
) -> ScanRecord:
    website = db.scalar(select(Website).where(Website.url == crawl.start_url))

    if website is None:
        website = Website(url=crawl.start_url)
        db.add(website)
        db.flush()

    health = site_health(crawl.pages)

    scan = ScanRecord(
        website=website,
        site_health=health.score,
        pages_scanned=crawl.pages_scanned,
        total_issues=crawl.total_issues,
        high_issues=health.severity.high,
        medium_issues=health.severity.medium,
        low_issues=health.severity.low,
        link_check_enabled=link_summary is not None,
        links_checked=link_summary.checked if link_summary else 0,
        broken_links_count=len(link_summary.broken) if link_summary else 0,
    )

    for page in crawl.pages:
        page_record = PageRecord(
            url=page.url,
            score=page_health_score(page),
            status_code=page.status_code,
            response_time_ms=page.response_time_ms,
            title=page.title,
            meta_description=page.meta_description,
            h1_count=page.h1_count,
            image_count=page.image_count,
            images_missing_alt=page.images_missing_alt,
            internal_link_count=len(page.internal_links),
            external_link_count=len(page.external_links),
        )

        for issue in page.issues:
            page_record.issues.append(
                IssueRecord(
                    severity=issue.severity,
                    category=issue.category,
                    message=issue.message,
                )
            )

        scan.pages.append(page_record)

    for error in crawl.errors:
        scan.crawl_errors.append(
            CrawlErrorRecord(url=error.url, message=error.message)
        )

    if link_summary is not None:
        for broken in link_summary.broken:
            scan.broken_links.append(
                BrokenLinkRecord(
                    url=broken.url,
                    status_code=broken.status_code,
                    response_time_ms=broken.response_time_ms,
                    error=broken.error,
                )
            )

    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan


def list_scans(db: Session, limit: int = 20) -> list[ScanRecord]:
    statement = (
        select(ScanRecord)
        .options(selectinload(ScanRecord.website))
        .order_by(desc(ScanRecord.created_at), desc(ScanRecord.id))
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def get_scan(db: Session, scan_id: int) -> ScanRecord | None:
    statement = (
        select(ScanRecord)
        .where(ScanRecord.id == scan_id)
        .options(
            selectinload(ScanRecord.website),
            selectinload(ScanRecord.pages).selectinload(PageRecord.issues),
            selectinload(ScanRecord.crawl_errors),
            selectinload(ScanRecord.broken_links),
        )
    )
    return db.scalar(statement)
