import os
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

import api_server


def test_health_is_public():
    with TestClient(api_server.app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_operational_route_fails_closed_without_configured_token(monkeypatch):
    monkeypatch.delenv("SCRAPER_API_TOKEN", raising=False)
    with TestClient(api_server.app) as client:
        response = client.post("/scrape", json={"url": "https://example.com"})
    assert response.status_code == 503


def test_operational_route_requires_bearer_token(monkeypatch):
    monkeypatch.setenv("SCRAPER_API_TOKEN", "test-secret-token")
    with TestClient(api_server.app) as client:
        response = client.post("/scrape", json={"url": "https://example.com"})
    assert response.status_code == 401


def test_scrape_endpoint_calls_existing_scraper(monkeypatch):
    monkeypatch.setenv("SCRAPER_API_TOKEN", "test-secret-token")
    expected = {"success": True, "url": "https://example.com"}
    with patch.object(
        api_server.AdvancedScraper,
        "scrape_url",
        new=AsyncMock(return_value=expected),
    ) as scrape:
        with TestClient(api_server.app) as client:
            response = client.post(
                "/scrape",
                json={"url": "https://example.com"},
                headers={"Authorization": "Bearer test-secret-token"},
            )
    assert response.status_code == 200
    assert response.json() == expected
    scrape.assert_awaited_once_with("https://example.com")


def test_crawl_depth_validation(monkeypatch):
    monkeypatch.setenv("SCRAPER_API_TOKEN", "test-secret-token")
    with TestClient(api_server.app) as client:
        response = client.post(
            "/crawl",
            json={"url": "https://example.com", "max_depth": 0},
            headers={"Authorization": "Bearer test-secret-token"},
        )
    assert response.status_code == 422
