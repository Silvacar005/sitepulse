from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from sitepulse.crawler import CrawlError, CrawlResult
from sitepulse.database import Base, Website
from sitepulse.linkcheck import LinkCheck, LinkCheckSummary
from sitepulse.persistence import get_scan, list_scans, save_scan
from sitepulse.scanner import ScanIssue, ScanResult


def make_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)()


def make_crawl() -> CrawlResult:
    page = ScanResult(
        url="https://example.com",
        status_code=200,
        response_time_ms=50,
        title="Example",
        meta_description="Example description",
        h1_count=1,
        image_count=2,
        images_missing_alt=1,
        internal_links=["https://example.com/about"],
        external_links=["https://openai.com"],
        issues=[
            ScanIssue(
                severity="medium",
                category="Accessibility",
                message="1 image(s) are missing useful alt text.",
            )
        ],
    )

    return CrawlResult(
        start_url="https://example.com",
        pages=[page],
        errors=[
            CrawlError(
                url="https://example.com/bad-page",
                message="Request failed",
            )
        ],
    )


def test_save_and_reload_full_scan():
    db = make_session()

    try:
        link_summary = LinkCheckSummary(
            checked=2,
            broken=[
                LinkCheck(
                    url="https://example.com/missing",
                    status_code=404,
                    response_time_ms=20,
                    broken=True,
                )
            ],
        )

        saved = save_scan(db, make_crawl(), link_summary=link_summary)
        loaded = get_scan(db, saved.id)

        assert loaded is not None
        assert loaded.website.url == "https://example.com"
        assert loaded.site_health == 90
        assert loaded.pages_scanned == 1
        assert loaded.total_issues == 1
        assert loaded.medium_issues == 1
        assert loaded.links_checked == 2
        assert loaded.broken_links_count == 1
        assert loaded.pages[0].meta_description == "Example description"
        assert loaded.pages[0].issues[0].category == "Accessibility"
        assert loaded.crawl_errors[0].url.endswith("/bad-page")
        assert loaded.broken_links[0].status_code == 404
    finally:
        db.close()


def test_reuses_website_and_lists_newest_scans():
    db = make_session()

    try:
        first = save_scan(db, make_crawl())
        second = save_scan(db, make_crawl())

        website_count = db.scalar(select(func.count()).select_from(Website))
        history = list_scans(db, limit=10)

        assert website_count == 1
        assert [item.id for item in history[:2]] == [second.id, first.id]
    finally:
        db.close()
