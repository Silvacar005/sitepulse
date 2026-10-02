from sitepulse.crawler import canonicalize_url, crawl_site
from sitepulse.scanner import ScanResult


def make_result(url: str, links: list[str]) -> ScanResult:
    return ScanResult(
        url=url,
        status_code=200,
        response_time_ms=10,
        title="Test",
        meta_description="Description",
        h1_count=1,
        image_count=0,
        images_missing_alt=0,
        internal_links=links,
        external_links=[],
        issues=[],
    )


def test_canonicalize_url_removes_query_and_fragment():
    assert canonicalize_url("https://example.com/about?x=1#team") == "https://example.com/about"


def test_crawler_uses_breadth_first_order_and_avoids_duplicates():
    pages = {
        "https://example.com": make_result(
            "https://example.com",
            [
                "https://example.com/about",
                "https://example.com/contact",
                "https://example.com/about#team",
            ],
        ),
        "https://example.com/about": make_result(
            "https://example.com/about",
            ["https://example.com/contact", "https://example.com/jobs"],
        ),
        "https://example.com/contact": make_result(
            "https://example.com/contact",
            [],
        ),
        "https://example.com/jobs": make_result(
            "https://example.com/jobs",
            [],
        ),
    }

    def fake_scan(url: str) -> ScanResult:
        return pages[url]

    result = crawl_site("example.com", max_pages=10, scan_page=fake_scan)

    assert [page.url for page in result.pages] == [
        "https://example.com",
        "https://example.com/about",
        "https://example.com/contact",
        "https://example.com/jobs",
    ]
    assert result.pages_scanned == 4
    assert result.errors == []


def test_crawler_respects_max_pages():
    pages = {
        "https://example.com": make_result(
            "https://example.com",
            ["https://example.com/a", "https://example.com/b"],
        ),
        "https://example.com/a": make_result("https://example.com/a", []),
        "https://example.com/b": make_result("https://example.com/b", []),
    }

    result = crawl_site(
        "https://example.com",
        max_pages=2,
        scan_page=lambda url: pages[url],
    )

    assert result.pages_scanned == 2
