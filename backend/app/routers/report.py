from fastapi import APIRouter, HTTPException
from app.models.report_model import create_event_summary

router = APIRouter(prefix="/report", tags=["Report"])

#Its hardcoded right now, but we can change it later to make it the output of the AI model
@router.post("/generate")
async def generate_report(data: dict):
    """
    Create a summary report for a booked event.

    Expected input:
    {
      "patient_name": "Jane Doe",
      "doctor_name": "Dr. Smith",
      "appointment": {"datetime": "2025-10-31T09:00Z", "duration": 30},
      "primary_concern": "Back pain",
      "medications": [
        {"name": "Ibuprofen", "dosage": "200mg", "frequency": "Twice daily"}
      ],
      "medical_history": "No chronic conditions.",
      "ai_insights": "Likely muscle strain.",
      "notes": "Follow up in 2 weeks."
    }
    """
    try:
        summary = create_event_summary(
            patient_name=data["patient_name"],
            doctor_name=data["doctor_name"],
            appointment=data["appointment"],
            primary_concern=data.get("primary_concern"),
            medications=data.get("medications"),
            medical_history=data.get("medical_history"),
            ai_insights=data.get("ai_insights"),
            notes=data.get("notes"),
        )

        return {"status": "success", "report": summary}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{event_id}")
async def get_report(event_id: int):
    """
    Mocked GET endpoint for testing and event preview.

    When you click an event on the calendar, this route will return
    a sample report. Later, you can replace it with a database lookup.
    """
    mock_report = {
        "report": {
            "title": f"Appointment Report #{event_id}",
            "patient_name": "Jane Doe",
            "doctor_name": "Dr. Smith",
            "primary_concern": "Back pain",
            "medical_history": "No chronic conditions.",
            "current_medications": [
                {"name": "Ibuprofen", "dosage": "200mg", "frequency": "Twice daily"}
            ],
            "ai_insights": "Likely muscle strain.",
            "notes": "Follow up in 2 weeks.",
        }
    }

    return mock_report