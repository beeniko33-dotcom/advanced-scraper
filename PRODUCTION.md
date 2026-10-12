# Production / Operational Notes – Advanced Scraper

## Phase 1 – Foundation

- [x] `.gitignore`
- [x] `requirements.txt`
- [x] README with responsible-use notice

## Phase 2 – Next level

This toolkit includes capabilities that must only be used on systems you own or have explicit authorization to test.

### Operational rules

1. **Authorized targets only.** Unauthorized scanning or credential testing is illegal.
2. Prefer rate limiting and respectful crawling for legitimate data collection.
3. Do not commit outputs, logs, or any harvested data.
4. Run inside a virtual environment; keep dependencies updated.

### Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python advanced_scraper.py
```

Treat this as a research / authorized-testing toolkit, not a general-purpose production service.
