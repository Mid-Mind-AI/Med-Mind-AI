# backend/app/calendar_store.py
"""
Calendar event storage and management module.

This module provides functions for managing calendar events using the Event and Events
types from app.schema.Events. It supports creating events, checking availability,
finding overlapping events, and filtering events by date range.

The module maintains a global EVENTS storage that persists events in memory.
Functions can optionally accept an Events object to operate on a different event
collection instead of the global storage.
"""

from datetime import datetime
from typing import Dict, List
from uuid import uuid4

from app.schema.Events import Event, Events

# Global storage for events
# This is the default event storage used when no events parameter is provided
EVENTS: Events = Events(events=[])


def _parse_iso(dt: str) -> datetime:
    """
    Parse an ISO 8601 formatted datetime string into a datetime object.
    
    Args:
        dt: ISO 8601 formatted string with timezone offset (e.g., "2025-01-07T14:00:00-08:00")
    
    Returns:
        datetime: Parsed datetime object
        
    Example:
        >>> _parse_iso("2025-01-07T14:00:00-08:00")
        datetime.datetime(2025, 1, 7, 14, 0, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=57600)))
    """
    return datetime.fromisoformat(dt)


def overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    """
    Check if two time ranges overlap.
    
    Two time ranges overlap if they have any time in common. This is determined by
    checking if the start of one range is before the end of the other, and vice versa.
    
    Args:
        a_start: Start time of the first range (datetime)
        a_end: End time of the first range (datetime)
        b_start: Start time of the second range (datetime)
        b_end: End time of the second range (datetime)
    
    Returns:
        bool: True if the ranges overlap, False otherwise
        
    Example:
        >>> overlaps(datetime(2025, 1, 7, 10, 0, 0), datetime(2025, 1, 7, 12, 0, 0), datetime(2025, 1, 7, 11, 0, 0), datetime(2025, 1, 7, 13, 0, 0))
        True
        >>> overlaps(datetime(2025, 1, 7, 10, 0, 0), datetime(2025, 1, 7, 11, 0, 0), datetime(2025, 1, 7, 12, 0, 0), datetime(2025, 1, 7, 13, 0, 0))
        False
    """
    return a_start < b_end and b_start < a_end


def list_month_events(time: datetime) -> Events:
    """
    Filter events that fall within a specified date range and timezone.
    
    Returns all events where:
    - The event start is on or after time
    - The event end is on or before time
    
    Args:
        time: The time to include events from (inclusive)
        events: The Events collection to search in
    
    Returns:
        Events: A new Events object containing only the filtered events
        
    Example:
        >>> from datetime import datetime
        >>> month_events = list_month_events(
        ...     datetime(2025, 1, 1),
        ...     datetime(2025, 1, 31),
        ...     "America/Los_Angeles",
        ...     events
        ... )
    """
    result: List[Event] = []
    for event in EVENTS.events:
        if event.start >= time and event.end <= time:
            result.append(event)
    return result


def get_events_between(start_time: datetime, end_time: datetime) -> List[Event]:
    """
    Find all events that overlap with a given time range.
    
    Returns events that:
    - Overlap with the specified start_time to end_time time range
    
    Args:
        start_time: Start time (datetime)
        end_time: End time (datetime)
    
    Returns:
        List[Event]: List of Event objects that overlap with the specified time range
        
    Example:
        >>> overlapping = get_events_between(
        ...     datetime(2025, 1, 7, 10, 0, 0),
        ...     datetime(2025, 1, 7, 12, 0, 0),
        ... )
    """
    return [ev for ev in EVENTS.events if overlaps(ev.start, ev.end, start_time, end_time)]


def check_availability(end_time: datetime, start_time: datetime) -> Dict:
    """
    Check if a time slot is available (has no conflicting events).
    
    Determines whether the specified time range is free by checking for overlapping
    events.
    
    Args:
        end_time: End time (datetime)
        start_time: Start time (datetime)
    
    Returns:
        Dict: A dictionary with:
            - "available": bool - True if the time slot is free, False if there are conflicts
            - "conflicts": List[Dict] - List of conflicting events (as dictionaries)
            
    Example:
        >>> result = check_availability(
        ...     datetime(2025, 1, 7, 10, 0, 0),
        ...     datetime(2025, 1, 7, 11, 0, 0),
        ... )
        >>> print(result["available"])
        True
        >>> print(result["conflicts"])
        []
    """
    busy = get_events_between(start_time, end_time)
    return {"available": len(busy) == 0, "conflicts": busy}


def create_event(event: Event) -> Event:
    """
    Create a new calendar event and add it to storage.
    
    Validates that:
    - The end time is after the start time
    - The time slot doesn't overlap with existing events
    
    
    Args:
        event: Dictionary containing event data with keys:
            - "title": str (required) - Event title
            - "start": str or datetime (required) - Start time (ISO string or datetime)
            - "end": str or datetime (required) - End time (ISO string or datetime)
            - "timezone": str (required) - Timezone string (e.g., "America/Los_Angeles")
            - "id": str (optional) - Event ID. If not provided, generates a UUID
            - "attendees": List[str] (optional) - List of attendee identifiers. Defaults to []
            - "notes": str (optional) - Event notes. Defaults to ""
    
    Returns:
        Event: The created Event object
        
    Raises:
        ValueError: If end time is not after start time, or if the time slot overlaps
                    with an existing event
    
    Example:
        >>> event_data = {
        ...     title: "Team Meeting",
        ...     start: datetime(2025, 1, 7, 10, 0, 0),
        ...     end: datetime(2025, 1, 7, 11, 0, 0),
        ...     attendees: ["user1", "user2"],
        ...     notes: "Quarterly planning"
        ... }
        >>> new_event = create_event(event)
        >>> print(new_event.title)
        Team Meeting
    """
    
   
    
    if event.end <= event.start:
        raise ValueError("end must be after start")
    
    if not check_availability(event.end, event.start)["available"]:
        raise ValueError("Requested time overlaps an existing event.")
    
    ev = Event(
        id=event.id or str(uuid4()),
        title=event.title,
        start=event.start,
        end=event.end,
        attendees=event.attendees,
        notes=event.notes,
        
    )
    # Add the event to the global EVENTS storage (add to db in real implementation)
    EVENTS.events.append(ev)
    return ev