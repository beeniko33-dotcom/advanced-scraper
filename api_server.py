import asyncio, pexpect, os, json, subprocess
from fastapi import FastAPI, Query
from pydantic import BaseModel
import uvicorn

app = FastAPI()

MODULES = {
    1: "Scrape URL", 2: "Crawl site", 3: "Image Search", 4: "Stealth Fetch",
    5: "Brute-Force Login", 6: "Directory Brute", 7: "Spider Emails",
    8: "SQLi Scan", 9: "XSS Scan", 10: "CSRF Check", 11: "Port Scan",
    12: "Subdomain Enum", 13: "CMD Injection", 14: "LFI/RFI Probe",
    15: "Rate-Limit Bypass", 16: "TCP Flood", 17: "Email Bomber",
    18: "SMS Bomber", 19: "OTP Brute-Force", 20: "Deep People Search",
    21: "AI Command", 23: "Reverse Shell Listener", 24: "Payload Generator",
    25: "Local PrivEsc Check", 26: "Persistence Tester"
}

async def run_interactive(module_id: int, target: str):
    try:
        child = pexpect.spawn('python advanced_scraper.py', encoding='utf-8', timeout=120)
        child.expect('Choice:')
        child.sendline(str(module_id))
        index = child.expect(['URL:', 'url:', 'IP:', 'Name:', 'Command:', 'Choice:', pexpect.EOF, pexpect.TIMEOUT], timeout=10)
        if index < 5:
            child.sendline(target)
        child.expect(['Choice:', pexpect.EOF], timeout=180)
        output = child.before + child.after
        child.terminate(force=True)
        return output
    except Exception as e:
        return f"Error executing module: {str(e)}"

@app.get("/")
async def root():
    return {"message": "Advanced Scraper API is live", "modules": MODULES}

@app.get("/run/{module_id}")
async def run_module(module_id: int, target: str = Query(..., description="Target URL/IP/Name")):
    if module_id not in MODULES:
        return {"error": "Invalid module ID"}
    output = await run_interactive(module_id, target)
    return {"module": MODULES[module_id], "target": target, "output": output}

@app.get("/scan/all")
async def scan_all(target: str = Query(..., description="Target for all modules")):
    results = {}
    for mid in [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,23,24,25,26]:
        results[mid] = await run_interactive(mid, target)
    return {"target": target, "results": results}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

@app.get("/think")
async def ai_think(target: str = Query(...)):
    import glob
    files = sorted(glob.glob(f"orchestration_{target.replace('.','_')}*.json"), reverse=True)
    if not files: return {"error": "No scan data found"}
    with open(files[0]) as f: data = json.load(f)
    from ai_brain import think_about
    return {"target": target, "ai_analysis": think_about(target, data)}

@app.post("/learn")
async def ai_learn(target: str, finding: str):
    from ai_brain import learn
    learn(target, finding)
    return {"status": "learned"}
