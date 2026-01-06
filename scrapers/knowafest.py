# scrapers/knowafest.py

import re
import json
import requests
import dateparser
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List

from core.base import BaseScraper
from core.schema import Event, EventDay
from core.registry import ScraperRegistry


class KnowafestChennaiScraper(BaseScraper):
    """
    Scraper for Knowafest Chennai city page
    + individual event pages
    """

    name = "knowafest_chennai"

    BASE_URL = "https://www.knowafest.com"
    CITY_URL = "https://www.knowafest.com/explore/city/Chennai"

    HEADERS = {
        "User-Agent": "EventListerBot/0.1 (educational)"
    }

    # ------------------------
    # Fetch city page
    # ------------------------
    def fetch(self) -> str:
        r = requests.get(self.CITY_URL, headers=self.HEADERS, timeout=20)
        r.raise_for_status()
        return r.text

    # ------------------------
    # Parse city page → event URLs
    # ------------------------
    def parse(self, city_html: str) -> List[Event]:
        soup = BeautifulSoup(city_html, "html.parser")

        table = soup.find("table", id="tablaDatos")
        if not table:
            return []

        events: List[Event] = []

        for row in table.find_all("tr", attrs={"itemscope": True}):
            onclick = row.get("onclick", "")
            match = re.search(r"window\.open\('(.+?)'", onclick)
            if not match:
                continue

            event_url = urljoin(self.BASE_URL, match.group(1))

            try:
                event = self.scrape_event_page(event_url)
                if event:
                    events.append(event)
            except Exception as e:
                print(f"[Knowafest] Failed to parse {event_url}: {e}")

        return events

    # ------------------------
    # Scrape individual event page
    # ------------------------
    def scrape_event_page(self, url: str) -> Event:
        r = requests.get(url, headers=self.HEADERS, timeout=20)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")

        # ------------------------
        # 1️⃣ JSON-LD (best source)
        # ------------------------
        json_ld = soup.find("script", type="application/ld+json")
        if json_ld:
            data = json.loads(json_ld.string)
            return self.parse_json_ld(data, url)

        # ------------------------
        # 2️⃣ Fallback HTML parsing
        # ------------------------
        return self.parse_html_page(soup, url)

    # ------------------------
    # JSON-LD parser
    # ------------------------
    def parse_json_ld(self, data: dict, url: str) -> Event:
        name = data.get("name")

        start = dateparser.parse(data.get("startDate")).date()
        end = dateparser.parse(data.get("endDate")).date()

        location = None
        institution = None

        for loc in data.get("location", []):
            if loc.get("@type") == "Place":
                institution = loc.get("name")
                addr = loc.get("address", {})
                location = addr.get("addressLocality")

        description = data.get("description")

        images = data.get("image", [])
        poster = images[0] if images else None

        organiser = data.get("organizer", {}).get("name")

        confidence = 0.9  # JSON-LD is authoritative

        return Event(
            event_name=name,
            event_type="conference",  # refined later by AI
            days=[EventDay(start_date=start, end_date=end)],
            event_link=url,
            source=self.name,
            confidence=confidence,

            event_location=location,
            institution=organiser or institution,
            description=description,
            poster=poster
        )

    # ------------------------
    # HTML fallback parser
    # ------------------------
    def parse_html_page(self, soup: BeautifulSoup, url: str) -> Event:
        title = soup.find("h3")
        name = title.get_text(strip=True) if title else None

        def dt_dd(label):
            dt = soup.find("dt", string=re.compile(label))
            return dt.find_next_sibling("dd").get_text(strip=True) if dt else None

        start_raw = dt_dd("Start Date")
        end_raw = dt_dd("End Date")

        start = dateparser.parse(start_raw).date() if start_raw else None
        end = dateparser.parse(end_raw).date() if end_raw else None

        location = dt_dd("Location")
        institution = dt_dd("Organizer")
        category = dt_dd("Category")

        description = None
        about = soup.find("h4", string="About Event")
        if about:
            description = about.find_next_sibling("p").get_text(strip=True)

        poster = None
        img = soup.find("img", class_="img-fluid")
        if img:
            poster = img.get("src")

        confidence = 0.7

        return Event(
            event_name=name,
            event_type=(category.lower() if category else "other"),
            days=[EventDay(start_date=start, end_date=end)],
            event_link=url,
            source=self.name,
            confidence=confidence,

            event_location=location,
            institution=institution,
            description=description,
            poster=poster
        )


# ------------------------
# Register scraper
# ------------------------
ScraperRegistry.register(KnowafestChennaiScraper)
