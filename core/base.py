# core/base.py
from abc import ABC, abstractmethod
from typing import List
from core.schema import Event

class BaseScraper(ABC):
    """
    Contract for all scrapers.
    Every scraper must:
    - fetch raw data
    - parse raw data into Event objects
    """

    # Each scraper MUST override this
    name: str = ""

    @abstractmethod
    def fetch(self):
        """
        Fetch raw data (HTML / JSON / API response).
        """
        pass

    @abstractmethod
    def parse(self, raw) -> List[Event]:
        """
        Parse raw data into a list of Event objects.
        """
        pass

    def run(self) -> List[Event]:
        """
        Standard execution pipeline for a scraper.
        """
        raw = self.fetch()
        events = self.parse(raw)
        return events
