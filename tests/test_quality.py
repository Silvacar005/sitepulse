from sitepulse.quality import count_severities, page_health_score, site_health
from sitepulse.scanner import ScanIssue, ScanResult


def make_result(issues: list[ScanIssue]) -> ScanResult:
    return ScanResult(
        url="https://example.com",
        status_code=200,
        response_time_ms=10,
        title="Example",
        meta_description="Description",
        h1_count=1,
        image_count=0,
        images_missing_alt=0,
        internal_links=[],
        external_links=[],
        issues=issues,
    )


def test_page_health_score_uses_severity_penalties():
    result = make_result([
        ScanIssue("high", "HTTP", "High"),
        ScanIssue("medium", "SEO", "Medium"),
        ScanIssue("low", "Structure", "Low"),
    ])

    assert page_health_score(result) == 67


def test_score_never_goes_below_zero():
    result = make_result([
        ScanIssue("high", "HTTP", "High")
        for _ in range(10)
    ])

    assert page_health_score(result) == 0


def test_site_health_averages_pages_and_counts_severity():
    clean = make_result([])
    issue_page = make_result([
        ScanIssue("medium", "SEO", "Medium"),
        ScanIssue("low", "Structure", "Low"),
    ])

    health = site_health([clean, issue_page])

    assert health.score == 94
    assert health.severity.high == 0
    assert health.severity.medium == 1
    assert health.severity.low == 1
