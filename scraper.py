import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import dateparser
from datetime import datetime
import re

BASE_URL = "https://www.knowafest.com"
CITY_URL = "https://www.knowafest.com/explore/city/Chennai"

HEADERS = {
    "User-Agent": "EventListerBot/0.1 (educational prototype)"
}

# ----------------------------
# Fetch page (handle redirects)
# ----------------------------
def fetch(url):
    r = requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
    r.raise_for_status()
    return r.text, r.url

# ----------------------------
# Extract events from table
# ----------------------------
def extract_events(html):
    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table", id="tablaDatos")
    if not table:
        print("[!] Event table not found")
        return []

    events = []

    for row in table.find_all("tr", attrs={"itemscope": True}):
        # --- URL from onclick ---
        onclick = row.get("onclick", "")
        match = re.search(r"window\.open\('(.+?)'", onclick)
        event_url = urljoin(BASE_URL, match.group(1)) if match else None

        # --- Core fields ---
        def get_text(selector):
            el = row.select_one(selector)
            return el.get_text(strip=True) if el else None

        start_raw = get_text("td[itemprop='startDate']")
        end_raw   = get_text("td[itemprop='endDate']")
        title     = get_text("td[itemprop='name']")

        fest_type_td = row.find("td", class_="optout")
        fest_type = fest_type_td.get_text(strip=True) if fest_type_td else None

        organiser = None
        location = None

        loc_span = row.select_one("span[itemprop='location']")
        if loc_span:
            organiser = loc_span.select_one("span[itemprop='name']")
            organiser = organiser.get_text(strip=True) if organiser else None

            city = loc_span.select_one("span[itemprop='addressLocality']")
            state = loc_span.select_one("span[itemprop='addressRegion']")
            location = ", ".join(
                x.get_text(strip=True)
                for x in [city, state] if x
            )

        # --- Date parsing ---
        start_date = dateparser.parse(start_raw).date() if start_raw else None
        end_date   = dateparser.parse(end_raw).date() if end_raw else None

        # --- Confidence heuristic ---
        confidence = 0.0
        if title: confidence += 0.3
        if start_date: confidence += 0.3
        if end_date: confidence += 0.2
        if organiser: confidence += 0.2

        events.append({
            "title": title,
            "type": fest_type,
            "organiser": organiser,
            "location": location,
            "start_date": start_date,
            "end_date": end_date,
            "url": event_url,
            "confidence": round(confidence, 2)
        })

    return events

# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    html, final_url = fetch(CITY_URL)
    print(f"[+] Crawling: {final_url}")

    events = extract_events(html)
    print(f"[+] Extracted {len(events)} events")

    # Sort by start date
    events.sort(key=lambda e: e["start_date"] or datetime.max.date())

    print("\n==== EVENTS (SORTED) ====\n")
    for e in events:
        print(f"Title      : {e['title']}")
        print(f"Type       : {e['type']}")
        print(f"Organiser  : {e['organiser']}")
        print(f"Location   : {e['location']}")
        print(f"Start Date : {e['start_date']}")
        print(f"End Date   : {e['end_date']}")
        print(f"Confidence : {e['confidence']}")
        print(f"URL        : {e['url']}")
        print("-" * 60)
