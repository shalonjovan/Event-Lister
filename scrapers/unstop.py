# scrapers/unstop.py

import requests
import dateparser
from bs4 import BeautifulSoup
from typing import List
from urllib.parse import urljoin

from core.base import BaseScraper
from core.schema import Event, EventDay
from core.registry import ScraperRegistry


class UnstopScraper(BaseScraper):
    """
    MVP scraper for Unstop public listings
    """

    name = "unstop"

    BASE_URL = "https://unstop.com"
    LISTING_URL = "https://unstop.com/hackathons"

    HEADERS = {
        "User-Agent": "EventListerBot/0.1 (educational)",
        "Accept-Language": "en-US,en;q=0.9"
    }

    # ------------------------
    # Fetch listing page
    # ------------------------
    def fetch(self) -> str:
        r = requests.get(self.LISTING_URL, headers=self.HEADERS, timeout=20)
        r.raise_for_status()
        return r.text

    # ------------------------
    # Parse listing page
    # ------------------------
    def parse(self, html: str) -> List[Event]:
        soup = BeautifulSoup(html, "html.parser")
        events: List[Event] = []

        # Unstop event cards
        cards = soup.select("a[href^='/hackathons/'], a[href^='/competitions/']")

        for card in cards:
            try:
                event = self.parse_card(card)
                if event:
                    events.append(event)
            except Exception:
                continue

        return events

    # ------------------------
    # Parse individual card
    # ------------------------
    def parse_card(self, card) -> Event | None:
        title_el = card.select_one("h2, h3")
        if not title_el:
            return None

        event_name = title_el.get_text(strip=True)

        event_url = urljoin(self.BASE_URL, card.get("href"))

        # Organizer
        organiser_el = card.find("p")
        institution = organiser_el.get_text(strip=True) if organiser_el else None

        # Date extraction (best-effort)
        date_text = card.get_text(" ", strip=True)
        parsed = dateparser.search.search_dates(date_text)
        days = []

        if parsed:
            start = parsed[0][1].date()
            end = parsed[-1][1].date()
            days = [EventDay(start_date=start, end_date=end)]
        else:
            return None  # mandatory field missing

        # Event type heuristic
        lowered = event_name.lower()
        if "hackathon" in lowered:
            event_type = "hackathon"
        elif "ctf" in lowered:
            event_type = "ctf"
        elif "workshop" in lowered:
            event_type = "workshop"
        else:
            event_type = "competition"

        confidence = 0.6  # listing-only confidence

        return Event(
            event_name=event_name,
            event_type=event_type,
            days=days,
            event_link=event_url,
            source=self.name,
            confidence=confidence,

            institution=institution,
            event_location=None,
            description=None
        )


# ------------------------
# Register scraper
# ------------------------
ScraperRegistry.register(UnstopScraper)
