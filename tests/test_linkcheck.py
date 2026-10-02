from sitepulse.linkcheck import LinkCheck, check_internal_links
from sitepulse.scanner import ScanResult


def make_page(url: str, links: list[str]) -> ScanResult:
    return ScanResult(
        url=url,
        status_code=200,
        response_time_ms=10,
        title="Example",
        meta_description="Description",
        h1_count=1,
        image_count=0,
        images_missing_alt=0,
        internal_links=links,
        external_links=[],
        issues=[],
    )


def test_link_checker_deduplicates_and_reports_broken_links():
    pages = [
        make_page(
            "https://example.com",
            ["https://example.com/about", "https://example.com/missing"],
        ),
        make_page(
            "https://example.com/about",
            ["https://example.com/missing"],
        ),
    ]

    def fake_check(url: str) -> LinkCheck:
        status = 404 if url.endswith("/missing") else 200
        return LinkCheck(
            url=url,
            status_code=status,
            response_time_ms=5,
            broken=status >= 400,
        )

    summary = check_internal_links(pages, checker=fake_check)

    assert summary.checked == 2
    assert len(summary.broken) == 1
    assert summary.broken[0].status_code == 404
