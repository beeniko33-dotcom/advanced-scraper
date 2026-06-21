import json, datetime, markdown, re, os
from jinja2 import Template

# Find the latest orchestration file
files = sorted([f for f in os.listdir('.') if f.startswith('orchestration_') and f.endswith('.json')], reverse=True)
if not files:
    print("No orchestration files found. Run orchestrator.py first.")
    exit()

with open(files[0], 'r') as f:
    data = json.load(f)

target = data.get("target", "unknown")
summary = {
    "target": target,
    "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    "emails": [],
    "ports": [],
    "vulns": []
}

for mid, output in data.get("results", {}).items():
    if "email" in output.lower():
        found_emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', output)
        summary["emails"].extend(found_emails)
    if "port" in output.lower():
        ports = re.findall(r'\d+/\w+', output)
        summary["ports"].extend(ports)
    if "vulnerable" in output.lower() or "sql" in output.lower() or "xss" in output.lower():
        summary["vulns"].append(f"Module {mid}: possible vulnerability found.")

summary["emails"] = list(set(summary["emails"]))
summary["ports"] = list(set(summary["ports"]))

template = Template("""
# Vulnerability Report for {{ target }}
**Generated**: {{ date }}

## Summary
- **Emails discovered**: {{ emails | join(', ') }}
- **Open ports detected**: {{ ports | join(', ') }}
- **Vulnerability hits**: {{ vulns | length }}

## Findings
{% for v in vulns %}
- {{ v }}
{% endfor %}

---
*Full JSON data saved in the orchestration file.*
""")

report = template.render(**summary)
with open("report.md", "w") as f:
    f.write(report)
html = markdown.markdown(report)
with open("report.html", "w") as f:
    f.write(html)
print("✅ Report generated: report.html")
