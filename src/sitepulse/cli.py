from __future__ import annotations

import argparse

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


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="sitepulse",
        description="Scan a webpage for basic SEO, accessibility, and structure issues.",
    )
    parser.add_argument("url", help="URL to scan, such as https://example.com")
    args = parser.parse_args()

    try:
        result = scan_url(args.url)
    except (ValueError, RuntimeError) as exc:
        parser.error(str(exc))

    print_report(result)


if __name__ == "__main__":
    main()
