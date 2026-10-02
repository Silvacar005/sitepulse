from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Callable
from urllib.parse import urlparse

from sitepulse.scanner import ScanResult, normalize_url, scan_url


@dataclass
class CrawlError:
    url: str
    message: str


@dataclass
class CrawlResult:
    start_url: str
    pages: list[ScanResult]
    errors: list[CrawlError]

    @property
    def pages_scanned(self) -> int:
        return len(self.pages)

    @property
    def total_issues(self) -> int:
        return sum(len(page.issues) for page in self.pages)


def canonicalize_url(url: str) -> str:
    """Remove fragments and query strings so duplicate page URLs collapse."""
    parsed = urlparse(url)
    cleaned = parsed._replace(fragment="", query="")
    return cleaned.geturl().rstrip("/") or cleaned.geturl()


def is_same_site(url: str, host: str) -> bool:
    """Return True when a URL belongs to the crawl's starting host."""
    return urlparse(url).netloc.lower() == host.lower()


def crawl_site(
    url: str,
    max_pages: int = 25,
    scan_page: Callable[[str], ScanResult] | None = None,
) -> CrawlResult:
    """Breadth-first crawl of pages on the same host.

    The crawler follows internal links discovered by the scanner, avoids
    duplicate pages, and stops after ``max_pages`` successful scans.
    """
    if max_pages < 1:
        raise ValueError("max_pages must be at least 1.")

    start_url = canonicalize_url(normalize_url(url))
    start_host = urlparse(start_url).netloc.lower()
    scanner = scan_page or scan_url

    queue: deque[str] = deque([start_url])
    queued: set[str] = {start_url}
    visited: set[str] = set()
    pages: list[ScanResult] = []
    errors: list[CrawlError] = []

    while queue and len(pages) < max_pages:
        current = queue.popleft()
        queued.discard(current)

        if current in visited:
            continue

        visited.add(current)

        try:
            result = scanner(current)
        except (RuntimeError, ValueError) as exc:
            errors.append(CrawlError(url=current, message=str(exc)))
            continue

        pages.append(result)

        for link in result.internal_links:
            candidate = canonicalize_url(link)

            if not candidate or not is_same_site(candidate, start_host):
                continue

            if candidate in visited or candidate in queued:
                continue

            queue.append(candidate)
            queued.add(candidate)

    return CrawlResult(start_url=start_url, pages=pages, errors=errors)
