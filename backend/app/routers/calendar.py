from app import calendar_store as cal
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime
from app.schema.Events import Event

router = APIRouter(prefix="/calendar", tags=["calendar"])


class AvailabilityRequest(BaseModel):
	start: str
	end: str
	timezone: str





@router.get("")
def get_calendar(time: datetime):
	events = cal.list_month_events(time)
	return {"events": events}


@router.post("/events")
def create_calendar_event(payload: Event):
	try:
		ev = cal.create_event(payload)
		return {"event": ev}
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.post("/availability/check")
def availability_check(payload: AvailabilityRequest):
	try:
		return cal.check_availability(payload.start, payload.end, payload.timezone)
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.get("/__debug")
def debug_calendar_store():
    import sys
    import types

    import calendar_store as cal
    return {
        "module_file": getattr(cal, "__file__", None),
        "has_list_month_events": hasattr(cal, "list_month_events"),
        "has_create_event": hasattr(cal, "create_event"),
        "dir_sample": [n for n in dir(cal) if not n.startswith("_")][:30],
        "sys_path_head": sys.path[:5],
        "module_type": str(type(cal)),
    }
