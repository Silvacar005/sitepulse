from __future__ import annotations

from dataclasses import dataclass

from sitepulse.scanner import ScanIssue, ScanResult


PENALTIES = {
    "high": 20,
    "medium": 10,
    "low": 3,
}


@dataclass(frozen=True)
class SeverityCounts:
    high: int = 0
    medium: int = 0
    low: int = 0

    @property
    def total(self) -> int:
        return self.high + self.medium + self.low


@dataclass(frozen=True)
class SiteHealth:
    score: int
    severity: SeverityCounts


def count_severities(issues: list[ScanIssue]) -> SeverityCounts:
    return SeverityCounts(
        high=sum(issue.severity == "high" for issue in issues),
        medium=sum(issue.severity == "medium" for issue in issues),
        low=sum(issue.severity == "low" for issue in issues),
    )


def page_health_score(result: ScanResult) -> int:
    """Return a deterministic 0-100 score based on detected issue severity."""
    penalty = sum(PENALTIES[issue.severity] for issue in result.issues)
    return max(0, 100 - penalty)


def site_health(pages: list[ScanResult]) -> SiteHealth:
    """Average page scores and aggregate severity counts for a crawl."""
    if not pages:
        return SiteHealth(score=0, severity=SeverityCounts())

    all_issues = [issue for page in pages for issue in page.issues]
    average = round(sum(page_health_score(page) for page in pages) / len(pages))

    return SiteHealth(
        score=average,
        severity=count_severities(all_issues),
    )
