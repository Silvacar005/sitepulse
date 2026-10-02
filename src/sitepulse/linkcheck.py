from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Callable

import requests

from sitepulse.scanner import ScanResult


@dataclass(frozen=True)
class LinkCheck:
    url: str
    status_code: int | None
    response_time_ms: int
    broken: bool
    error: str | None = None


@dataclass(frozen=True)
class LinkCheckSummary:
    checked: int
    broken: list[LinkCheck]


def check_link(url: str, timeout: int = 5) -> LinkCheck:
    """Check one HTTP link using HEAD with a GET fallback."""
    headers = {"User-Agent": "SitePulse/0.2 (+portfolio website quality scanner)"}
    started = perf_counter()

    try:
        response = requests.head(
            url,
            timeout=timeout,
            headers=headers,
            allow_redirects=True,
        )

        if response.status_code in {403, 405}:
            response = requests.get(
                url,
                timeout=timeout,
                headers=headers,
                allow_redirects=True,
                stream=True,
            )

        elapsed_ms = round((perf_counter() - started) * 1000)
        return LinkCheck(
            url=url,
            status_code=response.status_code,
            response_time_ms=elapsed_ms,
            broken=response.status_code >= 400,
        )
    except requests.RequestException as exc:
        elapsed_ms = round((perf_counter() - started) * 1000)
        return LinkCheck(
            url=url,
            status_code=None,
            response_time_ms=elapsed_ms,
            broken=True,
            error=str(exc),
        )


def check_internal_links(
    pages: list[ScanResult],
    max_links: int = 50,
    checker: Callable[[str], LinkCheck] | None = None,
) -> LinkCheckSummary:
    """Check unique internal links discovered during a crawl."""
    if max_links < 1:
        raise ValueError("max_links must be at least 1.")

    link_checker = checker or check_link
    links = sorted({link for page in pages for link in page.internal_links})
    selected = links[:max_links]
    results = [link_checker(link) for link in selected]

    return LinkCheckSummary(
        checked=len(results),
        broken=[result for result in results if result.broken],
    )
