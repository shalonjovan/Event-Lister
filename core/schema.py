# core/schema.py
from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List, Dict

# ----------------------------
# Supporting structures
# ----------------------------

@dataclass
class EventDay:
    start_date: date
    end_date: Optional[date] = None


@dataclass
class TeamSize:
    min: int
    max: Optional[int] = None  # None → fixed team size


# ----------------------------
# Main Event schema
# ----------------------------

@dataclass
class Event:
    # -------- Mandatory --------
    event_name: str
    event_type: str                    # hackathon, ctf, workshop, etc.
    days: List[EventDay]
    event_link: str                    # main page / website
    source: str                        # knowafest, unstop, instagram
    confidence: float                  # 0.0 – 1.0

    # -------- Optional --------
    event_location: Optional[str] = None
    institution: Optional[str] = None
    description: Optional[str] = None

    important_dates: Dict[str, date] = field(default_factory=dict)

    team_size: Optional[TeamSize] = None
    registration_fee: Optional[str] = None
    prize_money: Optional[str] = None

    registration_link: Optional[str] = None

    poster: Optional[str] = None       # image URL
    brochure: Optional[str] = None     # PDF URL

    contact_details: Optional[str] = None
    department: Optional[str] = None
    specialisation_or_theme: Optional[str] = None
