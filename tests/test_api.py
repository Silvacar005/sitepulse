from fastapi.testclient import TestClient

import sitepulse.api as api_module
from sitepulse.crawler import CrawlResult
from sitepulse.linkcheck import LinkCheck, LinkCheckSummary
from sitepulse.scanner import ScanIssue, ScanResult


client = TestClient(api_module.app)


def make_page() -> ScanResult:
    return ScanResult(
        url="https://example.com",
        status_code=200,
        response_time_ms=42,
        title="Example",
        meta_description="A description",
        h1_count=1,
        image_count=1,
        images_missing_alt=0,
        internal_links=["https://example.com/about"],
        external_links=["https://openai.com"],
        issues=[
            ScanIssue(
                severity="low",
                category="Structure",
                message="Heading hierarchy skips from H1 to H3.",
            )
        ],
    )


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_scan_endpoint_saves_and_returns_structured_results(monkeypatch):
    page = make_page()

    monkeypatch.setattr(
        api_module,
        "validate_public_url",
        lambda url: "https://example.com",
    )
    monkeypatch.setattr(
        api_module,
        "crawl_site",
        lambda url, max_pages: CrawlResult(
            start_url=url,
            pages=[page],
            errors=[],
        ),
    )
    monkeypatch.setattr(
        api_module,
        "check_internal_links",
        lambda pages, max_links: LinkCheckSummary(
            checked=1,
            broken=[
                LinkCheck(
                    url="https://example.com/missing",
                    status_code=404,
                    response_time_ms=20,
                    broken=True,
                )
            ],
        ),
    )

    response = client.post(
        "/api/scans",
        json={
            "url": "example.com",
            "max_pages": 5,
            "check_links": True,
            "max_links": 10,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data["id"], int)
    assert data["site_health"] == 97
    assert data["pages_scanned"] == 1
    assert data["total_issues"] == 1
    assert data["severity"] == {"high": 0, "medium": 0, "low": 1}
    assert data["pages"][0]["score"] == 97
    assert data["pages"][0]["meta_description"] == "A description"
    assert data["link_check"]["checked"] == 1
    assert data["link_check"]["broken_count"] == 1

    saved_response = client.get(f"/api/scans/{data['id']}")
    assert saved_response.status_code == 200
    assert saved_response.json()["id"] == data["id"]
    assert saved_response.json()["site_health"] == 97

    history_response = client.get("/api/scans?limit=100")
    assert history_response.status_code == 200
    history_ids = [item["id"] for item in history_response.json()["scans"]]
    assert data["id"] in history_ids


def test_scan_request_limits_are_validated():
    response = client.post(
        "/api/scans",
        json={"url": "https://example.com", "max_pages": 0},
    )

    assert response.status_code == 422


def test_private_url_is_rejected():
    response = client.post(
        "/api/scans",
        json={"url": "http://127.0.0.1"},
    )

    assert response.status_code == 400
    assert "public website" in response.json()["detail"].lower()


def test_missing_saved_scan_returns_404():
    response = client.get("/api/scans/999999999")

    assert response.status_code == 404
