"""Orchestrate the authenticated content-scraping API workflows."""
import json
import os
import time

import requests

API_URL = os.environ.get("SCRAPER_API_URL", "http://127.0.0.1:8000").rstrip("/")


def run_all(target):
    token = os.environ.get("SCRAPER_API_TOKEN", "")
    if not token:
        raise RuntimeError("Set SCRAPER_API_TOKEN before running the orchestrator.")

    headers = {"Authorization": f"Bearer {token}"}
    print(f"Starting authorized scrape and crawl workflows for: {target}")
    results = {}

    for name, route, payload in (
        ("scrape", "/scrape", {"url": target}),
        ("crawl", "/crawl", {"url": target, "max_depth": 2}),
    ):
        response = requests.post(
            f"{API_URL}{route}",
            json=payload,
            headers=headers,
            timeout=600,
        )
        response.raise_for_status()
        results[name] = response.json()

    filename = f"orchestration_{target.replace('.', '_')}_{int(time.time())}.json"
    with open(filename, "w", encoding="utf-8") as output:
        json.dump(results, output, indent=2, ensure_ascii=False)
    print(f"Scrape and crawl complete. Saved to {filename}")
    return results


if __name__ == "__main__":
    target = input("Enter an authorized target URL: ").strip()
    run_all(target)
