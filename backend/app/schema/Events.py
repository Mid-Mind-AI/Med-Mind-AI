from pydantic import BaseModel
from typing import List
from datetime import datetime
from typing import Optional, Dict

#Event Schema, this is the base event schema for the calendar, in prod link to User 
class Event(BaseModel):
    id: str
    title: str
    start: datetime
    end: datetime
    attendees: List[str]
    notes: str

#List of Events
class Events(BaseModel):
    events: List[Event]
    
    
class EventSummary(Event):
    primary_concern: Optional[str] = None
    current_medications: Optional[List[Dict[str, str]]] = None
    medical_history: Optional[str] = None
    ai_insights: Optional[str] = None