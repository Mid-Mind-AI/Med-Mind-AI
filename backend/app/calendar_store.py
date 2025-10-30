# backend/app/calendar_store.py
from datetime import datetime
from typing import Dict, List
from uuid import uuid4

# Canonical event shape stored in memory
# {"id": str, "title": str, "start": ISO8601, "end": ISO8601, "timezone": str, "attendees": [str], "notes": str}
EVENTS: List[Dict] = []

def _parse_iso(dt: str) -> datetime:
    # ISO 8601 with timezone offset expected, e.g. 2025-01-07T14:00:00-08:00
    return datetime.fromisoformat(dt)

def overlaps(a_start: str, a_end: str, b_start: str, b_end: str) -> bool:
    s1, e1 = _parse_iso(a_start), _parse_iso(a_end)
    s2, e2 = _parse_iso(b_start), _parse_iso(b_end)
    return s1 < e2 and s2 < e1

def list_month_events(year: int, month: int) -> List[Dict]:
    result = []
    for ev in EVENTS:
        dt = _parse_iso(ev["start"])
        if dt.year == year and dt.month == month:
            result.append(ev)
    return result

def get_events_between(start_iso: str, end_iso: str) -> List[Dict]:
    return [ev for ev in EVENTS if overlaps(ev["start"], ev["end"], start_iso, end_iso)]

def check_availability(start_iso: str, end_iso: str) -> Dict:
    busy = get_events_between(start_iso, end_iso)
    return {"available": len(busy) == 0, "conflicts": busy}

def create_event(event: Dict) -> Dict:
    if _parse_iso(event["end"]) <= _parse_iso(event["start"]):
        raise ValueError("end must be after start")
    if not check_availability(event["start"], event["end"])["available"]:
        raise ValueError("Requested time overlaps an existing event.")
    ev = {
        "id": event.get("id") or str(uuid4()),
        "title": event["title"],
        "start": event["start"],
        "end": event["end"],
        "timezone": event["timezone"],
        "attendees": event.get("attendees", []),
        "notes": event.get("notes", ""),
    }
    EVENTS.append(ev)
    return ev
