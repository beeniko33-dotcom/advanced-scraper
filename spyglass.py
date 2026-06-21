import subprocess, time, json
from advanced_scraper import DeepPeopleSearch
import asyncio

async def run(target_name, location):
    searcher = DeepPeopleSearch()
    result = await searcher.search(target_name, location)
    if result.get("phones"):
        msg = f"Found phone number: {result['phones'][0]}"
        subprocess.run(["espeak", msg])
        subprocess.run(["termux-vibrate", "-d", "1000"])
        print(msg)
    with open(f"spyglass_{target_name}.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    name = input("Enter name to search: ")
    loc = input("Enter location (optional): ")
    asyncio.run(run(name, loc))
