from __future__ import annotations

import argparse

from sitepulse.crawler import CrawlResult, crawl_site
from sitepulse.linkcheck import LinkCheckSummary, check_internal_links
from sitepulse.quality import count_severities, page_health_score, site_health
from sitepulse.scanner import ScanResult, scan_url


def print_report(result: ScanResult) -> None:
    health = page_health_score(result)
    severity = count_severities(result.issues)

    print()
    print("=" * 62)
    print("SITEPULSE REPORT")
    print("=" * 62)
    print(f"URL:                 {result.url}")
    print(f"Health score:        {health}/100")
    print(
        f"Issues:              {severity.high} high | "
        f"{severity.medium} medium | {severity.low} low"
    )
    print(f"HTTP status:         {result.status_code}")
    print(f"Response time:       {result.response_time_ms} ms")
    print(f"Title:               {result.title or 'Missing'}")
    print(f"Meta description:    {'Present' if result.meta_description else 'Missing'}")
    print(f"H1 headings:         {result.h1_count}")
    print(f"Images:              {result.image_count}")
    print(f"Images missing alt:  {result.images_missing_alt}")
    print(f"Internal links:      {len(result.internal_links)}")
    print(f"External links:      {len(result.external_links)}")
    print()

    if not result.issues:
        print("No issues detected by the current rule set.")
        return

    print(f"ISSUES ({len(result.issues)})")
    print("-" * 62)

    severity_order = {"high": 0, "medium": 1, "low": 2}

    for issue in sorted(result.issues, key=lambda item: severity_order[item.severity]):
        print(f"[{issue.severity.upper():6}] {issue.category}: {issue.message}")


def print_link_summary(summary: LinkCheckSummary) -> None:
    print()
    print("INTERNAL LINK CHECK")
    print("-" * 62)
    print(f"Links checked:        {summary.checked}")
    print(f"Broken links:         {len(summary.broken)}")

    for link in summary.broken:
        status = link.status_code if link.status_code is not None else "ERROR"
        suffix = f" - {link.error}" if link.error else ""
        print(f"[{status}] {link.url}{suffix}")


def print_crawl_report(
    result: CrawlResult,
    link_summary: LinkCheckSummary | None = None,
) -> None:
    health = site_health(result.pages)

    print()
    print("=" * 62)
    print("SITEPULSE CRAWL REPORT")
    print("=" * 62)
    print(f"Start URL:            {result.start_url}")
    print(f"Site health:          {health.score}/100")
    print(f"Pages scanned:        {result.pages_scanned}")
    print(f"Total issues:         {result.total_issues}")
    print(
        f"Severity:             {health.severity.high} high | "
        f"{health.severity.medium} medium | {health.severity.low} low"
    )
    print(f"Pages with errors:    {len(result.errors)}")
    print()

    for page in result.pages:
        score = page_health_score(page)
        print(f"{page.url}")
        print(
            f"  Score {score}/100 | HTTP {page.status_code} | "
            f"{page.response_time_ms} ms | {len(page.issues)} issue(s)"
        )
        for issue in page.issues:
            print(f"  - [{issue.severity.upper()}] {issue.category}: {issue.message}")

    if result.errors:
        print()
        print("CRAWL ERRORS")
        print("-" * 62)
        for error in result.errors:
            print(f"{error.url}: {error.message}")

    if link_summary is not None:
        print_link_summary(link_summary)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="sitepulse",
        description="Scan webpages for SEO, accessibility, and structure issues.",
    )
    parser.add_argument("url", help="URL to scan, such as https://example.com")
    parser.add_argument(
        "--crawl",
        action="store_true",
        help="Crawl internal links on the same website.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=25,
        help="Maximum pages to crawl (default: 25).",
    )
    parser.add_argument(
        "--check-links",
        action="store_true",
        help="Check unique internal links discovered during a crawl.",
    )
    parser.add_argument(
        "--max-links",
        type=int,
        default=50,
        help="Maximum internal links to check (default: 50).",
    )
    args = parser.parse_args()

    try:
        if args.crawl:
            result = crawl_site(args.url, max_pages=args.max_pages)
            link_summary = None

            if args.check_links:
                link_summary = check_internal_links(
                    result.pages,
                    max_links=args.max_links,
                )

            print_crawl_report(result, link_summary=link_summary)
        else:
            result = scan_url(args.url)
            print_report(result)
    except (ValueError, RuntimeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
