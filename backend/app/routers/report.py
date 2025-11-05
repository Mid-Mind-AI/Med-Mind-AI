from fastapi import APIRouter, HTTPException

from app.models.pre_visit_report import get_report
from app.models.report_model import create_event_summary
from app.services import calendar_store as cal

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
async def get_report_endpoint(event_id: str):
    """
    Get the pre-visit report for an event.

    Returns the actual report generated from pre-visit questions,
    or a placeholder if no report exists yet.
    """
    try:
        # Get event details
        event = cal.get_event_by_id(event_id)

        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        # Get the saved report
        saved_report = get_report(event_id)

        if saved_report:
            # Return the actual report
            return {
                "report": {
                    "title": f"Appointment Report - {event['patient_name']}",
                    "patient_name": event["patient_name"],
                    "doctor_name": event["doctor_name"],
                    "primary_concern": saved_report.get("primary_concern"),
                    "medical_history": saved_report.get("medical_history"),
                    "current_medications": saved_report.get("medications", []),
                    "ai_insights": saved_report.get("ai_insights"),
                    "suggested_questions": saved_report.get("suggested_questions", []),
                    "notes": saved_report.get("notes"),
                }
            }
        else:
            # Return placeholder if no report exists
            return {
                "report": {
                    "title": f"Appointment Report - {event['patient_name']}",
                    "patient_name": event["patient_name"],
                    "doctor_name": event["doctor_name"],
                    "primary_concern": None,
                    "medical_history": None,
                    "current_medications": [],
                    "ai_insights": None,
                    "suggested_questions": [],
                    "notes": "Pre-visit report not yet generated.",
                },
                "message": "No report available. Pre-visit questions may not have been completed."
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
