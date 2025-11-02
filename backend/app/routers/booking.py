from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app import calendar_store as cal

from ..models.booking_model import complete_booking_turn

router = APIRouter(prefix="/booking", tags=["booking"])

class ChatRequest(BaseModel):
    session_id: str
    user_message: str
    intent: str | None = None  # "check", "suggest", "create"
    # For check/create:
    start: str | None = None   # ISO
    end: str | None = None     # ISO
    timezone: str | None = None
    # For suggest:
    day: str | None = None     # "YYYY-MM-DD"
    slot_minutes: int | None = 30
    num_slots: int | None = 3

@router.post("/chat")
def booking_chat(payload: ChatRequest):
    # Always get a conversational reply from the model
    model_reply = complete_booking_turn([], payload.user_message)

    # Fast paths based on explicit intent from UI:
    if payload.intent == "check":
        if not (payload.start and payload.end):
            raise HTTPException(400, "start and end required")
        return {
            "reply": model_reply["content"],
            "availability": cal.check_availability(payload.start, payload.end),
        }

    if payload.intent == "create":
        if not (payload.start and payload.end and payload.timezone):
            raise HTTPException(400, "start, end, timezone required")
        try:
            ev = cal.create_event({
                "title": "Appointment",
                "start": payload.start,
                "end": payload.end,
                "timezone": payload.timezone,
                "attendees": [],
                "notes": "",
            })
            return {"reply": model_reply["content"], "event": ev}
        except Exception as e:
            raise HTTPException(400, str(e))

    if payload.intent == "suggest":
        # naive suggestion: scan the day for next N non-overlapping slots
        if not (payload.day and payload.slot_minutes and payload.num_slots):
            raise HTTPException(400, "day, slot_minutes, num_slots required")

        from datetime import datetime, timedelta
        from datetime import timezone as tz
        day = datetime.fromisoformat(payload.day + "T00:00:00+00:00")
        slot = timedelta(minutes=payload.slot_minutes)

        suggestions = []
        # 9am–5pm UTC day window (customize as needed)
        t = day.replace(hour=9, tzinfo=tz.utc)
        end_of_day = day.replace(hour=17, tzinfo=tz.utc)

        while t + slot <= end_of_day and len(suggestions) < payload.num_slots:
            s = t.isoformat()
            e = (t + slot).isoformat()
            if cal.check_availability(s, e)["available"]:
                suggestions.append({"start": s, "end": e})
            t += slot

        return {"reply": model_reply["content"], "suggestions": suggestions}

    # Default: just return the conversational reply
    return {"reply": model_reply["content"]}
