"""Period boundaries for persisted "reading of the day/year" lookups.

Daily spreads (tarot card of the day, rune of the day) persist for one
calendar day; the yearly rune spread persists for one calendar year. Both
boundaries are computed in UTC to stay aligned with the readings'
``created_at`` (which is ``datetime.utcnow()``), regardless of server TZ.
"""
from datetime import datetime


def period_start(period: str, now: datetime | None = None) -> datetime:
    """Start of the current period ("day" or "year") in UTC. A reading is the
    current one iff its created_at >= this boundary."""
    now = now or datetime.utcnow()
    if period == "year":
        return datetime(now.year, 1, 1)
    if period == "day":
        return datetime(now.year, now.month, now.day)
    raise ValueError(f"Unknown period: {period!r}")
