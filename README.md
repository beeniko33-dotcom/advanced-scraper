# Advanced Scraper Toolkit

Python-based advanced web scraper toolkit with supporting scripts for orchestration, API serving, reporting and utilities.

## Files

| File | Purpose |
|------|--------|
| `advanced_scraper.py` | Main scraper logic (~40 KB) |
| `api_server.py` | Simple API server |
| `orchestrator.py` | Coordination script |
| `report_gen.py` | Report generation |
| `spyglass.py` / `wardrive.py` | Utility scripts |
| `startup.sh` | Startup helper |

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
# Install any required packages (requests, beautifulsoup4, etc.) as needed
python advanced_scraper.py
```

## Notes

- `__pycache__` and log files should not be committed (now covered by `.gitignore`).
- This repository currently has no formal dependency file (`requirements.txt`). Consider adding one for reproducibility.

## Status

Functional core scraper present. Further cleanup, dependency pinning, and documentation improvements recommended.
