from __future__ import annotations

from dataclasses import asdict, dataclass
from time import perf_counter
from typing import Literal
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


Severity = Literal["high", "medium", "low"]


@dataclass
class ScanIssue:
    severity: Severity
    category: str
    message: str


@dataclass
class ScanResult:
    url: str
    status_code: int
    response_time_ms: int
    title: str | None
    meta_description: str | None
    h1_count: int
    image_count: int
    images_missing_alt: int
    internal_links: list[str]
    external_links: list[str]
    issues: list[ScanIssue]

    def to_dict(self) -> dict:
        data = asdict(self)
        data["issue_count"] = len(self.issues)
        return data


def normalize_url(url: str) -> str:
    """Add a scheme when the user enters a bare domain."""
    url = url.strip()

    if not url:
        raise ValueError("URL cannot be empty.")

    if "://" not in url:
        url = f"https://{url}"

    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Please enter a valid HTTP or HTTPS URL.")

    return url


def classify_links(base_url: str, soup: BeautifulSoup) -> tuple[list[str], list[str]]:
    """Return unique internal and external HTTP(S) links."""
    base_host = urlparse(base_url).netloc.lower()
    internal: set[str] = set()
    external: set[str] = set()

    for anchor in soup.find_all("a", href=True):
        href = anchor.get("href", "").strip()

        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue

        absolute = urljoin(base_url, href)
        parsed = urlparse(absolute)

        if parsed.scheme not in {"http", "https"}:
            continue

        cleaned = parsed._replace(fragment="").geturl()

        if parsed.netloc.lower() == base_host:
            internal.add(cleaned)
        else:
            external.add(cleaned)

    return sorted(internal), sorted(external)


def analyze_html(
    url: str,
    html: str,
    *,
    status_code: int = 200,
    response_time_ms: int = 0,
) -> ScanResult:
    """Analyze HTML without performing a network request."""
    soup = BeautifulSoup(html, "html.parser")
    issues: list[ScanIssue] = []

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else None

    if not title:
        issues.append(
            ScanIssue(
                severity="high",
                category="SEO",
                message="Page is missing a title.",
            )
        )

    meta_tag = soup.find(
        "meta",
        attrs={"name": lambda value: value and value.lower() == "description"},
    )
    meta_description = meta_tag.get("content", "").strip() if meta_tag else None

    if not meta_description:
        issues.append(
            ScanIssue(
                severity="medium",
                category="SEO",
                message="Page is missing a meta description.",
            )
        )

    h1_tags = soup.find_all("h1")
    h1_count = len(h1_tags)

    if h1_count == 0:
        issues.append(
            ScanIssue(
                severity="medium",
                category="Structure",
                message="Page does not contain an H1 heading.",
            )
        )
    heading_tags = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    heading_levels = [int(tag.name[1]) for tag in heading_tags]

    for previous, current in zip(heading_levels, heading_levels[1:]):
        if current > previous + 1:
            issues.append(
                ScanIssue(
                    severity="low",
                    category="Structure",
                    message=(
                        f"Heading hierarchy skips from H{previous} to H{current}."
                    ),
                )
            )
            break

    images = soup.find_all("img")
    missing_alt = sum(
        1
        for image in images
        if image.get("alt") is None or not image.get("alt", "").strip()
    )

    if missing_alt:
        issues.append(
            ScanIssue(
                severity="medium",
                category="Accessibility",
                message=f"{missing_alt} image(s) are missing useful alt text.",
            )
        )

    internal_links, external_links = classify_links(url, soup)

    if status_code >= 400:
        issues.append(
            ScanIssue(
                severity="high",
                category="HTTP",
                message=f"Page returned HTTP {status_code}.",
            )
        )

    return ScanResult(
        url=url,
        status_code=status_code,
        response_time_ms=response_time_ms,
        title=title,
        meta_description=meta_description,
        h1_count=h1_count,
        image_count=len(images),
        images_missing_alt=missing_alt,
        internal_links=internal_links,
        external_links=external_links,
        issues=issues,
    )


def scan_url(url: str, timeout: int = 10) -> ScanResult:
    """Download a page and analyze its HTML."""
    normalized = normalize_url(url)

    headers = {
        "User-Agent": "SitePulse/0.3 (+portfolio website quality scanner)"
    }

    started = perf_counter()

    try:
        response = requests.get(
            normalized,
            timeout=timeout,
            headers=headers,
            allow_redirects=True,
        )
    except requests.RequestException as exc:
        raise RuntimeError(f"Could not scan {normalized}: {exc}") from exc

    elapsed_ms = round((perf_counter() - started) * 1000)

    return analyze_html(
        response.url,
        response.text,
        status_code=response.status_code,
        response_time_ms=elapsed_ms,
    )
