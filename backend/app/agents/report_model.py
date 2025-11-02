from datetime import datetime
from typing import List, Dict, Optional
from app.schema.Events import Event, EventSummary

def create_event_summary(
    event: Event,
    primary_concern: Optional[str] = None,
    medications: Optional[List[Dict[str, str]]] = None,
    medical_history: Optional[str] = None,
    ai_insights: Optional[str] = None,
) -> EventSummary:
    """
    Create an EventSummary from an Event with additional medical context.
    
    This function extends an Event with medical information to create a comprehensive
    EventSummary suitable for display in calendar popups.
    
    Args:
        event: The base Event object containing calendar information (id, title, start, end, attendees, notes)
        primary_concern: Main reason for the visit/appointment
        medications: List of current medications, each as a dict with keys like 'name', 'dosage', 'frequency'
        medical_history: Relevant medical history information
        ai_insights: AI-generated insights about the appointment or patient
        
    Returns:
        EventSummary: An EventSummary object that extends the Event with medical context fields
        
    Example:
        >>> from app.schema.Events import Event
        >>> from datetime import datetime
        >>> event = Event(
        ...     id="123",
        ...     title="Follow-up",
        ...     start=datetime(2025, 1, 7, 10, 0),
        ...     end=datetime(2025, 1, 7, 10, 30),
        ...     attendees=["patient@example.com"],
        ...     notes="Regular checkup"
        ... )
        >>> summary = create_event_summary(
        ...     event,
        ...     primary_concern="Pain management",
        ...     medications=[{"name": "Ibuprofen", "dosage": "200mg", "frequency": "twice daily"}],
        ...     medical_history="Previous surgery in 2020",
        ...     ai_insights="Patient showing improvement"
        ... )
    """
    #TODO Create an LLM Agent to generate the summary 
    
    # Create EventSummary by copying all Event fields and adding summary fields
    summary = EventSummary(
        # Inherited Event fields
        id=event.id,
        title=event.title,
        start=event.start,
        end=event.end,
        attendees=event.attendees,
        notes=event.notes,
        # Additional EventSummary fields
        primary_concern=primary_concern,
        current_medications=medications,
        medical_history=medical_history,
        ai_insights=ai_insights,
    )
    
    return summary

def format_medications(medications: List[Dict[str, str]]) -> str:
    """Helper function to format medications for display"""
    if not medications:
        return "No current medications"
    
    return "\n".join([
        f"• {med['name']} - {med['dosage']} ({med['frequency']})"
        for med in medications
    ])