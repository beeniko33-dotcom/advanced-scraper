import requests, json, time, os

API_URL = "http://127.0.0.1:8000"

def run_all(target):
    print(f"🔥 Starting full orchestration on: {target}")
    resp = requests.get(f"{API_URL}/scan/all", params={"target": target}, timeout=600)
    if resp.status_code == 200:
        data = resp.json()
        filename = f"orchestration_{target.replace('.','_')}_{int(time.time())}.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"✅ Full scan complete. Saved to {filename}")
    else:
        print(f"❌ API Error: {resp.status_code}")

if __name__ == "__main__":
    target = input("Enter target (URL/IP/Name): ")
    run_all(target)
