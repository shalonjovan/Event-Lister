# core/registry.py
from typing import Dict, Type
from core.base import BaseScraper

class ScraperRegistry:
    """
    Central registry for all scrapers.
    Scrapers register themselves here.
    """

    _registry: Dict[str, Type[BaseScraper]] = {}

    @classmethod
    def register(cls, scraper_cls: Type[BaseScraper]):
        if not issubclass(scraper_cls, BaseScraper):
            raise TypeError("Scraper must inherit from BaseScraper")

        if not scraper_cls.name:
            raise ValueError("Scraper must define a non-empty 'name' attribute")

        cls._registry[scraper_cls.name] = scraper_cls

    @classmethod
    def get(cls, name: str) -> Type[BaseScraper]:
        return cls._registry.get(name)

    @classmethod
    def all(cls) -> Dict[str, Type[BaseScraper]]:
        return dict(cls._registry)

    @classmethod
    def create(cls, name: str) -> BaseScraper:
        scraper_cls = cls.get(name)
        if not scraper_cls:
            raise KeyError(f"Scraper '{name}' not found")
        return scraper_cls()
