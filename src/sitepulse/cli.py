from __future__ import annotations

import argparse

from sitepulse.crawler import CrawlResult, crawl_site
from sitepulse.scanner import ScanResult, scan_url


def print_report(result: ScanResult) -> None:
    print()
    print("=" * 58)
    print("SITEPULSE REPORT")
    print("=" * 58)
    print(f"URL:                 {result.url}")
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
    print("-" * 58)

    severity_order = {"high": 0, "medium": 1, "low": 2}

    for issue in sorted(result.issues, key=lambda item: severity_order[item.severity]):
        print(f"[{issue.severity.upper():6}] {issue.category}: {issue.message}")


def print_crawl_report(result: CrawlResult) -> None:
    print()
    print("=" * 58)
    print("SITEPULSE CRAWL REPORT")
    print("=" * 58)
    print(f"Start URL:            {result.start_url}")
    print(f"Pages scanned:        {result.pages_scanned}")
    print(f"Total issues:         {result.total_issues}")
    print(f"Pages with errors:    {len(result.errors)}")
    print()

    for page in result.pages:
        print(f"{page.url}")
        print(
            f"  HTTP {page.status_code} | {page.response_time_ms} ms | "
            f"{len(page.issues)} issue(s)"
        )
        for issue in page.issues:
            print(f"  - [{issue.severity.upper()}] {issue.category}: {issue.message}")

    if result.errors:
        print()
        print("CRAWL ERRORS")
        print("-" * 58)
        for error in result.errors:
            print(f"{error.url}: {error.message}")


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
    args = parser.parse_args()

    try:
        if args.crawl:
            result = crawl_site(args.url, max_pages=args.max_pages)
            print_crawl_report(result)
        else:
            result = scan_url(args.url)
            print_report(result)
    except (ValueError, RuntimeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
