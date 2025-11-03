from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app import calendar_store as cal

from ..models.booking_model import complete_booking_turn

router = APIRouter(prefix="/booking", tags=["booking"])

# ============================================================================
# CONSTANTS
# ============================================================================

DEFAULT_SLOT_MINUTES = 30
DEFAULT_NUM_SLOTS = 3
SUGGESTION_START_HOUR = 9  # 9am UTC
SUGGESTION_END_HOUR = 17   # 5pm UTC


# ============================================================================
# REQUEST MODELS
# ============================================================================

class ChatRequest(BaseModel):
    """Request model for booking chat endpoint."""
    session_id: str = Field(..., description="Unique session identifier")
    user_message: str = Field(..., description="User's message/query")
    intent: str | None = Field(
        None,
        description="Optional intent: 'check', 'suggest', or 'create'"
    )

    # Fields for check/create intents
    start: str | None = Field(None, description="Start time in ISO 8601 format")
    end: str | None = Field(None, description="End time in ISO 8601 format")
    timezone: str | None = Field(None, description="Timezone string")

    # Fields for suggest intent
    day: str | None = Field(None, description="Date in YYYY-MM-DD format")
    slot_minutes: int | None = Field(
        DEFAULT_SLOT_MINUTES,
        description="Duration of each slot in minutes"
    )
    num_slots: int | None = Field(
        DEFAULT_NUM_SLOTS,
        description="Number of suggestions to return"
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def validate_check_intent(payload: ChatRequest) -> None:
    """Validate required fields for check intent.

    Raises:
        HTTPException: If start or end is missing
    """
    if not (payload.start and payload.end):
        raise HTTPException(
            status_code=400,
            detail="start and end are required for check intent"
        )


def validate_create_intent(payload: ChatRequest) -> None:
    """Validate required fields for create intent.

    Raises:
        HTTPException: If start, end, or timezone is missing
    """
    if not (payload.start and payload.end and payload.timezone):
        raise HTTPException(
            status_code=400,
            detail="start, end, and timezone are required for create intent"
        )


def validate_suggest_intent(payload: ChatRequest) -> None:
    """Validate required fields for suggest intent.

    Raises:
        HTTPException: If day, slot_minutes, or num_slots is missing
    """
    if not (payload.day and payload.slot_minutes and payload.num_slots):
        raise HTTPException(
            status_code=400,
            detail="day, slot_minutes, and num_slots are required for suggest intent"
        )


def generate_time_suggestions(
    day: str,
    slot_minutes: int,
    num_slots: int
) -> List[Dict[str, str]]:
    """Generate available time slot suggestions for a given day.

    Args:
        day: Date string in YYYY-MM-DD format
        slot_minutes: Duration of each slot in minutes
        num_slots: Maximum number of suggestions to return

    Returns:
        List of suggestion dictionaries with 'start' and 'end' ISO timestamps
    """
    day_dt = datetime.fromisoformat(day + "T00:00:00+00:00")
    slot_delta = timedelta(minutes=slot_minutes)

    suggestions = []
    current = day_dt.replace(hour=SUGGESTION_START_HOUR, tzinfo=timezone.utc)
    end_of_day = day_dt.replace(hour=SUGGESTION_END_HOUR, tzinfo=timezone.utc)

    while current + slot_delta <= end_of_day and len(suggestions) < num_slots:
        start_iso = current.isoformat()
        end_iso = (current + slot_delta).isoformat()

        if cal.check_availability(start_iso, end_iso)["available"]:
            suggestions.append({"start": start_iso, "end": end_iso})

        current += slot_delta

    return suggestions


# ============================================================================
# INTENT HANDLERS
# ============================================================================

def handle_check_intent(
    payload: ChatRequest,
    model_reply: Dict[str, Any]
) -> Dict[str, Any]:
    """Handle check availability intent.

    Args:
        payload: Chat request payload
        model_reply: AI model reply dictionary

    Returns:
        Response dictionary with reply and availability info
    """
    validate_check_intent(payload)

    availability = cal.check_availability(payload.start, payload.end)

    return {
        "reply": model_reply["content"],
        "availability": availability,
    }


def handle_create_intent(
    payload: ChatRequest,
    model_reply: Dict[str, Any]
) -> Dict[str, Any]:
    """Handle create event intent.

    Args:
        payload: Chat request payload
        model_reply: AI model reply dictionary

    Returns:
        Response dictionary with reply and created event

    Raises:
        HTTPException: If event creation fails
    """
    validate_create_intent(payload)

    try:
        event_data = {
            "patient_name": "Patient",  # TODO: Extract from payload or session
            "phone_number": "",  # TODO: Extract from payload or session
            "doctor_name": "",  # TODO: Extract from payload or session
            "start": payload.start,
            "end": payload.end,
            "timezone": payload.timezone,
            "notes": "",
        }
        event = cal.create_event(event_data)

        return {
            "reply": model_reply["content"],
            "event": event,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def handle_suggest_intent(
    payload: ChatRequest,
    model_reply: Dict[str, Any]
) -> Dict[str, Any]:
    """Handle suggest alternative times intent.

    Args:
        payload: Chat request payload
        model_reply: AI model reply dictionary

    Returns:
        Response dictionary with reply and suggestions
    """
    validate_suggest_intent(payload)

    suggestions = generate_time_suggestions(
        payload.day,
        payload.slot_minutes,
        payload.num_slots
    )

    return {
        "reply": model_reply["content"],
        "suggestions": suggestions,
    }


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/chat")
def booking_chat(payload: ChatRequest) -> Dict[str, Any]:
    """Handle booking chat requests with optional intents.

    This endpoint processes user messages through the AI booking model
    and optionally executes specific intents like checking availability,
    creating events, or suggesting times.

    Args:
        payload: Chat request with user message and optional intent data

    Returns:
        Response dictionary with AI reply and optional intent results
    """
    # Get AI model reply for conversational response
    model_reply = complete_booking_turn([], payload.user_message)

    if payload.intent == "check":
        return handle_check_intent(payload, model_reply)

    if payload.intent == "create":
        return handle_create_intent(payload, model_reply)

    if payload.intent == "suggest":
        return handle_suggest_intent(payload, model_reply)

    # Default: return just the conversational reply
    return {"reply": model_reply["content"]}
