# Advanced Scraper Toolkit

Python-based advanced web scraper toolkit with supporting scripts for orchestration, API serving, reporting and utilities.

## Important – Responsible Use

This toolkit contains modules intended for legitimate security testing, research, and data extraction **only on systems you own or have explicit written permission to test**.  
Unauthorized scanning, credential testing, or exploitation of third-party systems is illegal. Use at your own risk and only for authorized purposes.

## Files

| File | Purpose |
|------|--------|
| `advanced_scraper.py` | Main scraper / toolkit logic |
| `api_server.py` | Simple API server |
| `orchestrator.py` | Coordination script |
| `report_gen.py` | Report generation |
| `spyglass.py` / `wardrive.py` | Utility scripts |
| `startup.sh` | Startup helper |
| `requirements.txt` | Core Python dependencies |

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python advanced_scraper.py
```

## Dependencies

See `requirements.txt`:
- aiohttp, beautifulsoup4, lxml
- colorama, rich

## Status

Core scraper and toolkit present. Use only on authorized targets.
