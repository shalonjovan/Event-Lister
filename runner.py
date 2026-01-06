# runner.py
from core.registry import ScraperRegistry
from datetime import date

# Import scrapers so they register themselves
import scrapers.knowafest  # noqa: F401


OUTPUT_FILE = "events.txt"


def format_event(event) -> str:
    lines = []
    lines.append("=" * 50)
    lines.append(f"Event Name        : {event.event_name}")
    lines.append(f"Event Type        : {event.event_type.capitalize()}")
    lines.append(f"Institution       : {event.institution}")
    lines.append(f"Location          : {event.event_location}")
    lines.append("")
    lines.append("Event Days:")
    for day in event.days:
        lines.append(f"  - Start Date    : {day.start_date}")
        lines.append(f"    End Date      : {day.end_date}")
    lines.append("")
    lines.append(f"Description       : {event.description}")
    lines.append(f"Poster            : {event.poster}")
    lines.append(f"Event Link        : {event.event_link}")
    lines.append(f"Source            : {event.source}")
    lines.append(f"Confidence        : {event.confidence:.2f}")
    lines.append("=" * 50)
    lines.append("")
    return "\n".join(lines)


def main():
    all_events = []

    registry = ScraperRegistry.all()

    if not registry:
        print("[!] No scrapers registered")
        return

    for name, scraper_cls in registry.items():
        print(f"[+] Running scraper: {name}")
        scraper = scraper_cls()
        try:
            events = scraper.run()
            all_events.extend(events)
            print(f"    -> Collected {len(events)} events")
        except Exception as e:
            print(f"    [!] Error in {name}: {e}")

    # Sort by start date
    all_events.sort(
        key=lambda e: e.days[0].start_date if e.days else date.max
    )

    # Write to file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for event in all_events:
            f.write(format_event(event))

    print(f"\n[✓] Saved {len(all_events)} events to '{OUTPUT_FILE}'")


if __name__ == "__main__":
    main()
