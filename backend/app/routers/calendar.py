<<<<<<< HEAD
import sys

=======
from app import calendar_store as cal
>>>>>>> d051a845697a869663f56674831db10d6c37a800
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app import calendar_store as cal

router = APIRouter(prefix="/calendar", tags=["calendar"])


class AvailabilityRequest(BaseModel):
	start: str
	end: str
	timezone: str


class EventCreate(BaseModel):
	patient_name: str
	phone_number: str
	start: str
	end: str
	timezone: str
	notes: str | None = None


@router.get("")
def get_calendar(month: str = Query(..., pattern=r"^\d{4}-\d{2}$")):
	# month: "YYYY-MM"
	year, mon = month.split("-")
	events = cal.list_month_events(int(year), int(mon))
	return {"events": events}


@router.post("/events")
def create_calendar_event(payload: EventCreate):
	try:
		ev = cal.create_event(payload.model_dump())
		return {"event": ev}
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.post("/availability/check")
def availability_check(payload: AvailabilityRequest):
	try:
		return cal.check_availability(payload.start, payload.end)
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.get("/__debug")
def debug_calendar_store():

    return {
        "module_file": getattr(cal, "__file__", None),
        "has_list_month_events": hasattr(cal, "list_month_events"),
        "has_create_event": hasattr(cal, "create_event"),
        "dir_sample": [n for n in dir(cal) if not n.startswith("_")][:30],
        "sys_path_head": sys.path[:5],
        "module_type": str(type(cal)),
    }
