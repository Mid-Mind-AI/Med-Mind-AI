# backend/app/calendar_store.py
from datetime import datetime
from typing import Dict, List, TypedDict
from uuid import uuid4
import json
from pathlib import Path


# Canonical event shape stored in memory
class Event(TypedDict):
    id: str
    patient_name: str
    phone_number: str
    doctor_name: str
    start: str
    end: str
    timezone: str
    notes: str

EVENTS: List[Event] = []

# Simple JSON persistence (dev-friendly)
_DATA_DIR = Path(__file__).parent.parent / "data"
_DATA_DIR.mkdir(exist_ok=True)
_EVENTS_FILE = _DATA_DIR / "calendar_events.json"

def _load_events_from_disk() -> List[Event]:
    try:
        if _EVENTS_FILE.exists():
            raw = json.loads(_EVENTS_FILE.read_text())
            # Basic validation/shape normalization
            events: List[Event] = []
            for ev in raw if isinstance(raw, list) else []:
                if all(k in ev for k in [
                    "id", "patient_name", "phone_number", "doctor_name",
                    "start", "end", "timezone",
                ]):
                    events.append({
                        "id": str(ev["id"]),
                        "patient_name": ev["patient_name"],
                        "phone_number": ev["phone_number"],
                        "doctor_name": ev["doctor_name"],
                        "start": ev["start"],
                        "end": ev["end"],
                        "timezone": ev["timezone"],
                        "notes": ev.get("notes", ""),
                    })
            return events
    except Exception:
        # If the file is corrupt or unreadable, start fresh (dev resilience)
        pass
    return []

def _save_events_to_disk(events: List[Event]) -> None:
    try:
        _EVENTS_FILE.write_text(json.dumps(events, indent=2))
    except Exception:
        # Ignore save failures in dev; will just be in-memory
        pass

# Initialize from disk on import
EVENTS = _load_events_from_disk()

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

def _list_month_events(events: List[Event], year: int, month: int) -> List[Event]:
    result: List[Event] = []
    for ev in events:
        dt = _parse_iso(ev["start"])
        if dt.year == year and dt.month == month:
            result.append(ev)
    return result

def _get_events_between(events: List[Event], start_iso: str, end_iso: str) -> List[Event]:
    return [ev for ev in events if overlaps(ev["start"], ev["end"], start_iso, end_iso)]

def _check_availability(events: List[Event], start_iso: str, end_iso: str) -> Dict:
    busy = _get_events_between(events, start_iso, end_iso)
    return {"available": len(busy) == 0, "conflicts": busy}

def _create_event(events: List[Event], event: Dict) -> Event:
    if _parse_iso(event["end"]) <= _parse_iso(event["start"]):
        raise ValueError("end must be after start")
    if not _check_availability(events, event["start"], event["end"])["available"]:
        raise ValueError("Requested time overlaps an existing event.")

    ev: Event = {
        "id": event.get("id") or str(uuid4()),
        "patient_name": event["patient_name"],
        "phone_number": event["phone_number"],
        "doctor_name": event["doctor_name"],
        "start": event["start"],
        "end": event["end"],
        "timezone": event["timezone"],
        "notes": event.get("notes", ""),
    }
    events.append(ev)
    _save_events_to_disk(events)
    return ev


# Public API functions that use the global EVENTS list
def list_month_events(year: int, month: int) -> List[Event]:
    """List all events for a specific month."""
    return _list_month_events(EVENTS, year, month)


def check_availability(start_iso: str, end_iso: str) -> Dict:
    """Check if a time slot is available."""
    return _check_availability(EVENTS, start_iso, end_iso)


def create_event(event: Dict) -> Event:
    """Create a new event and add it to the global EVENTS list."""
    return _create_event(EVENTS, event)


def get_event_by_id(event_id: str) -> Event | None:
    """Get an event by its ID."""
    for event in EVENTS:
        if event["id"] == event_id:
            return event
    return None
