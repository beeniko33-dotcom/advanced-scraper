import subprocess, time, json, requests
import os

API_URL = "http://127.0.0.1:8000"
SEEN_NETWORKS = set()

def get_wifi_info():
    try:
        out = subprocess.check_output(["termux-wifi-connectioninfo"]).decode()
        return json.loads(out)
    except:
        return None

def scan_target(gateway_ip):
    print(f"🔍 New network detected: {gateway_ip}")
    payload = {"url": f"http://{gateway_ip}"}
    try:
        r = requests.post(f"{API_URL}/scan", json=payload, timeout=10)
        print(f"✅ Scan triggered for {gateway_ip}")
    except Exception as e:
        print(f"❌ Failed to scan: {e}")

while True:
    info = get_wifi_info()
    if info and info.get("ssid"):
        gateway = info.get("gateway_ip", "192.168.1.1")
        ssid = info.get("ssid", "")
        key = f"{ssid}_{gateway}"
        if key not in SEEN_NETWORKS:
            SEEN_NETWORKS.add(key)
            scan_target(gateway)
    time.sleep(30)
