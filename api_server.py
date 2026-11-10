"""Authenticated HTTP interface for the supported scraping workflows.

The interactive CLI remains the full local operator interface. This API exposes
content scraping workflows only; it is not a remote command-execution surface.
"""
import hmac
import os
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from advanced_scraper import AdvancedScraper

app = FastAPI(
    title="Advanced Scraper API",
    description="Authenticated web scraping, crawling, and image search API.",
    version="2.0.0",
)
bearer = HTTPBearer(auto_error=False)


def require_api_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer),
) -> None:
    """Fail closed unless a configured bearer token matches."""
    expected = os.environ.get("SCRAPER_API_TOKEN", "")
    if not expected:
        raise HTTPException(
            status_code=503,
            detail="API authentication is not configured by the operator.",
        )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Authentication required.")
    if not hmac.compare_digest(credentials.credentials, expected):
        raise HTTPException(status_code=401, detail="Invalid credentials.")


class ScrapeRequest(BaseModel):
    url: str = Field(..., min_length=1, max_length=2048)


class CrawlRequest(BaseModel):
    url: str = Field(..., min_length=1, max_length=2048)
    max_depth: int = Field(default=2, ge=1, le=10)


class ImageSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    count: int = Field(default=5, ge=1, le=50)


@app.get("/")
async def root():
    return {
        "message": "Advanced Scraper API",
        "status": "available",
        "authentication": "required for operational endpoints",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/scrape", dependencies=[Depends(require_api_token)])
async def scrape(request: ScrapeRequest):
    return await AdvancedScraper().scrape_url(request.url)


@app.post("/crawl", dependencies=[Depends(require_api_token)])
async def crawl(request: CrawlRequest):
    return await AdvancedScraper().crawl(request.url, max_depth=request.max_depth)


@app.post("/images", dependencies=[Depends(require_api_token)])
async def image_search(request: ImageSearchRequest):
    return await AdvancedScraper().search_images(
        request.query, count=request.count
    )


if __name__ == "__main__":
    import uvicorn

    host = os.environ.get("SCRAPER_API_HOST", "127.0.0.1")
    port = int(os.environ.get("SCRAPER_API_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
