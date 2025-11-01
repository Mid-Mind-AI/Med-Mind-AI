from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel

class EventSummary(BaseModel):
    title: str
    datetime: str
    duration: int
    patient_name: str
    doctor_name: str
    status: str = "Scheduled"
    primary_concern: Optional[str] = None
    current_medications: Optional[List[Dict[str, str]]] = None
    medical_history: Optional[str] = None
    ai_insights: Optional[str] = None
    notes: Optional[str] = None

def create_event_summary(
    patient_name: str,
    doctor_name: str,
    appointment: Dict,
    primary_concern: Optional[str] = None,
    medications: Optional[List[Dict[str, str]]] = None,
    medical_history: Optional[str] = None,
    ai_insights: Optional[str] = None,
    notes: Optional[str] = None
) -> Dict:
    """
    Create a summary for an event popup in the calendar.
    
    Args:
        patient_name: Name of the patient
        doctor_name: Name of the doctor
        appointment: Dictionary containing appointment details
        primary_concern: Main reason for visit
        medications: List of current medications
        medical_history: Relevant medical history
        ai_insights: AI-generated insights
        notes: Additional notes
        
    Returns:
        Dict: Structured summary for the event popup
    """
    summary = EventSummary(
        title=f"Appointment - {patient_name}",
        datetime=appointment['datetime'],
        duration=appointment.get('duration', 30),
        patient_name=patient_name,
        doctor_name=doctor_name,
        primary_concern=primary_concern,
        current_medications=medications,
        medical_history=medical_history,
        ai_insights=ai_insights,
        notes=notes
    )
    
    return summary.dict()

def format_medications(medications: List[Dict[str, str]]) -> str:
    """Helper function to format medications for display"""
    if not medications:
        return "No current medications"
    
    return "\n".join([
        f"• {med['name']} - {med['dosage']} ({med['frequency']})"
        for med in medications
    ])