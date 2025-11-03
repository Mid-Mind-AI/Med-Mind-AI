import sys
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app import calendar_store as cal

router = APIRouter(prefix="/calendar", tags=["calendar"])

# ============================================================================
# REQUEST MODELS
# ============================================================================

class AvailabilityRequest(BaseModel):
	start: str
	end: str
	timezone: str


class EventCreate(BaseModel):
	patient_name: str
	phone_number: str
	doctor_name: str
	start: str
	end: str
	timezone: str
	notes: str | None = None


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.get("")
def get_calendar(month: str = Query(..., pattern=r"^\d{4}-\d{2}$")) -> Dict[str, Any]:
	"""Get all events for a specific month.

	Args:
		month: Month in "YYYY-MM" format (e.g., "2025-01")

	Returns:
		Dictionary with 'events' key containing list of events for the month

	Example:
		GET /calendar?month=2025-01
	"""
	year, mon = month.split("-")
	events = cal.list_month_events(int(year), int(mon))
	return {"events": events}


@router.post("/events")
def create_calendar_event(payload: EventCreate) -> Dict[str, Any]:
	"""Create a new calendar event/appointment.

	Args:
		payload: Event creation request with patient info and time details

	Returns:
		Dictionary with 'event' key containing the created event details

	Raises:
		HTTPException: If event creation fails (e.g., time slot not available)

	Example:
		POST /calendar/events
		{
			"patient_name": "John Doe",
			"phone_number": "555-1234",
			"start": "2025-01-15T14:00:00+00:00",
			"end": "2025-01-15T14:30:00+00:00",
			"timezone": "UTC",
			"notes": "Follow-up appointment"
		}
	"""
	try:
		event = cal.create_event(payload.model_dump())
		return {"event": event}
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.post("/availability/check")
def availability_check(payload: AvailabilityRequest) -> Dict[str, Any]:
	"""Check if a time slot is available for booking.

	Args:
		payload: Availability request with start and end times

	Returns:
		Dictionary with 'available' (bool) and 'conflicts' (list) keys

	Raises:
		HTTPException: If the request is invalid

	Example:
		POST /calendar/availability/check
		{
			"start": "2025-01-15T14:00:00+00:00",
			"end": "2025-01-15T14:30:00+00:00",
			"timezone": "UTC"
		}
	"""
	try:
		return cal.check_availability(payload.start, payload.end)
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.get("/__debug")
def debug_calendar_store() -> Dict[str, Any]:
	"""Debug endpoint to inspect calendar store state.

	This endpoint provides diagnostic information about the calendar store
	module, including its file path, available functions, system path,
	and current events. Useful for debugging and development.

	Returns:
		Dictionary with debug information including:
		- module_file: Path to the calendar_store module
		- has_list_month_events: Whether the function exists
		- has_create_event: Whether the function exists
		- dir_sample: Sample of module attributes
		- sys_path_head: First 5 entries in sys.path
		- module_type: Type of the module object
		- events_count: Number of events currently stored
		- all_events: List of all events in the store
	"""
	return {
		"module_file": getattr(cal, "__file__", None),
		"has_list_month_events": hasattr(cal, "list_month_events"),
		"has_create_event": hasattr(cal, "create_event"),
		"dir_sample": [n for n in dir(cal) if not n.startswith("_")][:30],
		"sys_path_head": sys.path[:5],
		"module_type": str(type(cal)),
		"events_count": len(cal.EVENTS),
		"all_events": cal.EVENTS,
	}
