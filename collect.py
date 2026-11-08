import csv
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

HEADERS = {"User-Agent": "WebDataScience/1.0 (INFO 4617; haal5146@colorado.edu)"}
DELAY = 5
CACHE = Path("cache")
DATA = Path("data")
FORBES_URL = "https://web.archive.org/web/20210810104048id_/https://www.forbes.com/forbesapi/org/cloud100/2021/position/true.json?limit=2000"
CDX_URL = "https://web.archive.org/cdx/search/cdx"
QUARTERS = [f"{year}Q{q}" for year in range(2019, 2026) for q in range(1, 5)]

WEBSITES = {
    "Canva": "canva.com",
    "Checkout.com": "checkout.com",
    "Attentive": "attentivemobile.com",
    "Celonis": "celonis.com",
    "Hopin": "hopin.com",
    "Gong.io": "gong.io",
    "Fivetran": "fivetran.com",
    "Scale AI": "scale.com",
    "Calendly": "calendly.com",
    "DataRobot": "datarobot.com",
    "MessageBird": "messagebird.com",
    "Snyk": "snyk.io",
    "Cohesity": "cohesity.com",
    "Icertis": "icertis.com",
    "Notion": "notion.so",
    "LaunchDarkly": "launchdarkly.com",
    "Cedar": "cedar.com",
    "Lucid": "lucidchart.com",
    "Razorpay": "razorpay.com",
    "Airwallex": "airwallex.com",
    "OutSystems": "outsystems.com",
    "Weave": "getweave.com",
    "Cockroach Labs": "cockroachlabs.com",
    "HighRadius": "highradius.com",
    "MX": "mx.com",
    "Kong": "konghq.com",
    "Contentful": "contentful.com",
    "Rapyd": "rapyd.net",
    "Mambu": "mambu.com",
    "TripActions": "tripactions.com",
    "Grafana Labs": "grafana.com",
    "Riskified": "riskified.com",
    "ActiveCampaign": "activecampaign.com",
    "Flutterwave": "flutterwave.com",
    "Entrata": "entrata.com",
    "Workato": "workato.com",
    "BigID": "bigid.com",
    "FanRuan Software": "fanruan.com",
    "OwnBackup": "ownbackup.com",
    "Socure": "socure.com",
    "Jushuitan (JST)": "jushuitan.com",
    "Shippo": "goshippo.com",
    "VTS": "vts.com",
    "Loom": "useloom.com",
    "6sense": "6sense.com",
    "Papaya Global": "papayaglobal.com",
    "Culture Amp": "cultureamp.com",
    "Axonius": "axonius.com",
}


def get(url, params=None):
    for attempt in range(6):
        try:
            response = requests.get(url, params=params, headers=HEADERS, timeout=120)
        except requests.exceptions.RequestException as error:
            print(f"  {type(error).__name__}, waiting 60 seconds", flush=True)
            time.sleep(60)
            continue
        time.sleep(DELAY)
        if response.status_code in (429, 502, 503, 504):
            wait = response.headers.get("Retry-After", "60")
            wait = int(wait) if wait.isdigit() else 60
            print(f"  status {response.status_code}, waiting {wait} seconds", flush=True)
            time.sleep(wait)
            continue
        return response
    return None


def quarter_of(timestamp):
    return f"{timestamp[:4]}Q{(int(timestamp[4:6]) - 1) // 3 + 1}"


def load_companies():
    path = CACHE / "forbes_cloud100_2021.json"
    if not path.exists():
        response = get(FORBES_URL)
        response.raise_for_status()
        path.write_bytes(response.content)
    listing = json.loads(path.read_text())["organizationList"]["organizationsLists"]

    companies = []
    for item in sorted(listing, key=lambda item: item["rank"]):
        name = item["organizationName"]
        site = WEBSITES.get(name) or item.get("webSite")
        homepage = re.sub(r"^https?://(www\.)?", "", site).strip("/")
        companies.append({
            "rank": item["rank"],
            "company": name,
            "slug": re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-"),
            "industry": item.get("industry"),
            "homepage": homepage,
            "homepage_source": "added" if name in WEBSITES else "forbes",
        })

    DATA.mkdir(exist_ok=True)
    with open(DATA / "companies.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(companies[0]))
        writer.writeheader()
        writer.writerows(companies)
    return companies


def captures_for(company):
    path = CACHE / "cdx" / f"{company['slug']}.json"
    if not path.exists():
        params = {
            "url": company["homepage"],
            "from": "2019",
            "to": "2025",
            "output": "json",
            "fl": "timestamp,original,statuscode,mimetype",
            "filter": "mimetype:text/html",
            "collapse": "timestamp:8",
        }
        response = get(CDX_URL, params)
        if response is None or response.status_code != 200:
            status = None if response is None else response.status_code
            print(f"{company['company']}: CDX failed ({status})", flush=True)
            return []
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(response.text or "[]")
    rows = json.loads(path.read_text() or "[]")
    return [dict(zip(rows[0], row)) for row in rows[1:]] if rows else []


def select_quarters(companies):
    selected = []
    for company in companies:
        captures = captures_for(company)
        for quarter in QUARTERS:
            in_quarter = [c for c in captures if quarter_of(c["timestamp"]) == quarter]
            ok = [c for c in in_quarter if c["statuscode"] == "200"]
            moved = [c for c in in_quarter if c["statuscode"].startswith("3")]
            choice = (ok or moved or [None])[0]
            selected.append({
                "slug": company["slug"],
                "quarter": quarter,
                "timestamp": choice["timestamp"] if choice else "",
                "original": choice["original"] if choice else "",
                "statuscode": choice["statuscode"] if choice else "",
            })
    with open(CACHE / "selected.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(selected[0]))
        writer.writeheader()
        writer.writerows(selected)
    return selected


def fetch_pages(selected, quarters):
    log_path = CACHE / "fetch_log.csv"
    done = set()
    if log_path.exists():
        with open(log_path) as f:
            for row in csv.DictReader(f):
                if row["status"] == "200" or row["status"].startswith("4"):
                    done.add((row["slug"], row["timestamp"]))
    new_log = not log_path.exists()

    todo = [s for s in selected if s["timestamp"] and s["quarter"] in quarters and (s["slug"], s["timestamp"]) not in done]
    todo.sort(key=lambda s: (quarters.index(s["quarter"]), s["slug"]))
    print(f"{len(todo)} pages to fetch", flush=True)

    with open(log_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["slug", "quarter", "timestamp", "status", "final_url", "bytes", "fetched_at"])
        if new_log:
            writer.writeheader()
        for n, s in enumerate(todo, 1):
            url = f"https://web.archive.org/web/{s['timestamp']}id_/{s['original']}"
            response = get(url)
            status = "error" if response is None else str(response.status_code)
            if status == "200":
                path = CACHE / "html" / s["slug"] / f"{s['timestamp']}.html"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(response.content)
            writer.writerow({
                "slug": s["slug"],
                "quarter": s["quarter"],
                "timestamp": s["timestamp"],
                "status": status,
                "final_url": "" if response is None else response.url,
                "bytes": 0 if response is None else len(response.content),
                "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            })
            f.flush()
            print(f"[{n}/{len(todo)}] {s['quarter']} {s['slug']} {status}", flush=True)


if __name__ == "__main__":
    CACHE.mkdir(exist_ok=True)
    companies = load_companies()
    selected = select_quarters(companies)
    found = sum(1 for s in selected if s["timestamp"])
    print(f"{len(companies)} companies, {found} of {len(selected)} company-quarters have a capture", flush=True)
    if len(sys.argv) > 1 and sys.argv[1] == "Q4":
        quarters = [q for q in QUARTERS if q.endswith("Q4")]
    else:
        quarters = [q for q in QUARTERS if q.endswith("Q4")] + [q for q in QUARTERS if not q.endswith("Q4")]
    fetch_pages(selected, quarters)
