# backend/app/calendar_store.py
from datetime import datetime
from typing import Dict, List, TypedDict
from uuid import uuid4


# Canonical event shape stored in memory
class Event(TypedDict):
    id: str
    patient_name: str
    phone_number: str
    start: str
    end: str
    timezone: str
    notes: str

EVENTS: List[Event] = []

def _parse_iso(dt: str) -> datetime:
    # ISO 8601 with timezone offset expected, e.g. 2025-01-07T14:00:00-08:00
    # Handle 'Z' suffix (UTC) by converting to +00:00
    if dt.endswith('Z'):
        dt = dt[:-1] + '+00:00'
    return datetime.fromisoformat(dt)

def overlaps(a_start: str, a_end: str, b_start: str, b_end: str) -> bool:
    s1, e1 = _parse_iso(a_start), _parse_iso(a_end)
    s2, e2 = _parse_iso(b_start), _parse_iso(b_end)
    return s1 < e2 and s2 < e1

def list_month_events(events: List[Event], year: int, month: int) -> List[Event]:
    result: List[Event] = []
    for ev in events:
        dt = _parse_iso(ev["start"])
        if dt.year == year and dt.month == month:
            result.append(ev)
    return result

def get_events_between(events: List[Event], start_iso: str, end_iso: str) -> List[Event]:
    return [ev for ev in events if overlaps(ev["start"], ev["end"], start_iso, end_iso)]

def check_availability(events: List[Event], start_iso: str, end_iso: str) -> Dict:
    busy = get_events_between(events, start_iso, end_iso)
    return {"available": len(busy) == 0, "conflicts": busy}

def create_event(events: List[Event], event: Event) -> Event:
    if _parse_iso(event["end"]) <= _parse_iso(event["start"]):
        raise ValueError("end must be after start")
    if not check_availability(events, event["start"], event["end"])["available"]:
        raise ValueError("Requested time overlaps an existing event.")

    ev: Event = {
        "id": event.get("id") or str(uuid4()),
        "patient_name": event["patient_name"],
        "phone_number": event["phone_number"],
        "start": event["start"],
        "end": event["end"],
        "timezone": event["timezone"],
        "notes": event.get("notes", ""),
    }
    events.append(ev)
    return ev
