# Advanced Scraper Toolkit

Python-based toolkit for authorized web scraping, crawling, extraction, image search, reporting, and research workflows.

## Responsible use

Use the toolkit only on websites and systems you own or are explicitly authorized to access. Respect applicable terms, privacy requirements, and access controls. Do not use it to collect private personal data, bypass access controls, attack accounts, disrupt services, or access systems without permission.

## Core CLI setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python advanced_scraper.py
```

The local interactive CLI remains the primary interface for the toolkit's locally operated workflows.

## Authenticated API setup

Install API dependencies:

```bash
pip install -r requirements-api.txt
```

Create a local `.env` from `.env.example`, set a long random `SCRAPER_API_TOKEN`, and load those variables into the process environment. Do not commit `.env` or paste its token into chat.

Generate a token with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Start the API locally:

```bash
python api_server.py
```

The API binds to `127.0.0.1:8000` by default. Keep that default for local use. For remote access, place the service behind a properly configured TLS reverse proxy and protect the token as a secret.

### API routes

- `GET /health` — public liveness check; does not expose operational data.
- `POST /scrape` — scrape a URL.
- `POST /crawl` — crawl a site with an explicit depth.
- `POST /images` — search images for a query.

All operational routes require `Authorization: Bearer <SCRAPER_API_TOKEN>`. If the token is not configured, operational routes fail closed with HTTP 503. Missing or invalid credentials receive HTTP 401.

Example:

```bash
curl -X POST http://127.0.0.1:8000/scrape \\
  -H "Authorization: Bearer $SCRAPER_API_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"url":"https://example.com"}'
```

The HTTP API intentionally exposes the supported content-scraping workflows, not arbitrary interactive command execution. The full set of local CLI features is not deleted by this API change.

## API tests

```bash
pip install -r requirements-api-dev.txt
pytest -q
```

## Dependencies

- Core: aiohttp, beautifulsoup4, lxml, colorama, rich
- API: FastAPI, Uvicorn
- API tests: pytest, httpx

