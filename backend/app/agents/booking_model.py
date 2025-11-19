"""
Booking agent module using LangChain for calendar event management.

This module provides a conversational agent that can check availability,
suggest times, and create calendar events using LangChain's agent framework.
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone as tz

from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from app.schema.Events import Event
from app.services.calendar_store import create_event, check_availability

# Load environment variables from .env
load_dotenv('.env.local')

# Configuration
API_BASE = os.getenv("CAL_API_BASE", "http://localhost:8000")
BOOKING_MODEL = os.getenv("BOOKING_MODEL", "openai/gpt-5-nano")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")



@tool
def check_calendar_availability(start: str, end: str, timezone: str) -> str:
    """
    use this tool to check if a time range is available (has no conflicting events).
    Check if a time range is available (has no conflicting events).

    Args:
        start: ISO 8601 formatted start time with timezone offset (e.g., "2025-01-07T10:00:00-08:00")
        end: ISO 8601 formatted end time with timezone offset
        timezone: Timezone string (e.g., "America/Los_Angeles")

    Returns:
        Dict: A dictionary with:
            - "available": bool - True if the time slot is free, False if there are conflicts
            - "conflicts": List[Event] - List of conflicting events
    """
    result = check_availability(start, end, timezone)
    return result


@tool
def suggest_times(day: str, slot_minutes: int = 30, num_slots: int = 3) -> str:
    """
    use this tool to suggest free time slots within a day window (UTC 9-17).

    Args:
        day: Date string in YYYY-MM-DD format (UTC day)
        slot_minutes: Duration of each slot in minutes (default: 30)
        num_slots: Maximum number of slots to suggest (default: 3)

    Returns:
        Dict: A dictionary with:
            - "suggestions": List[Dict] - List of suggested time slots
            Each suggestion should have:
            - "start": str - ISO 8601 formatted start time
            - "end": str - ISO 8601 formatted end time
    """
    day_dt = datetime.fromisoformat(day + "T00:00:00+00:00")
    slot = timedelta(minutes=int(slot_minutes))
    n = int(num_slots)

    t = day_dt.replace(hour=9, tzinfo=tz.utc)
    end_of_day = day_dt.replace(hour=17, tzinfo=tz.utc)

    suggestions = []
    while t + slot <= end_of_day and len(suggestions) < n:
        s = t.isoformat()
        e = (t + slot).isoformat()

        avail_result = check_availability(s, e, "UTC")

        if isinstance(avail_result, dict) and avail_result.get("available"):
            suggestions.append({"start": s, "end": e})

        t += slot

    return {"suggestions": suggestions}


@tool
def create_calendar_event(event: Event) -> Event:
    """
    Create a calendar event after explicit confirmation.

    Args:
        event: Event object to create
        The event object should have the following fields:
        - title: str
        - start: datetime
        - end: datetime
        - timezone: str
        - attendees: List[str]
        - notes: str

    Returns:
        Event: The created Event object
    """

    return create_event(event)


# Create the list of tools
TOOLS = [check_calendar_availability, suggest_times, create_calendar_event]

# Create system prompt
SYSTEM_PROMPT = (
    "You are Sarah, a warm and friendly clinic receptionist. "
    "Use tools to check availability, suggest alternatives, and book events. "
    "Never say something is booked until create_event succeeds. "
    "Keep replies under 2 sentences and confirm title and timezone."
)

# Initialize the LLM lazily to avoid errors if API key is not set at import time
_booking_model = None
_agent = None


def get_booking_model():
    """Get or create the booking model instance."""
    global _booking_model
    if _booking_model is None:
        # Fallback to OPENAI_API_KEY if OPENROUTER_API_KEY is not set
        api_key = OPENROUTER_API_KEY or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "Either OPENROUTER_API_KEY or OPENAI_API_KEY must be set in environment variables"
            )
        _booking_model = ChatOpenAI(
            model=BOOKING_MODEL,
            base_url=OPENROUTER_BASE_URL,
            api_key=api_key,
            temperature=0.3,
        )
    return _booking_model


def get_agent():
    """Get or create the agent instance."""
    global _agent
    if _agent is None:
        model = get_booking_model()
        _agent = create_agent(
            model,
            tools=TOOLS,
            system_prompt=SYSTEM_PROMPT
        )
    return _agent


def complete_booking_turn(chat_history: List[Dict[str, str]], user_message: str) -> Dict[str, str]:
    """
    Process a booking message through the booking agent.

    Args:
        chat_history: Previous messages in format [{"role": "user/assistant", "content": "..."}]
        user_message: Current user message

    Returns:
        Dictionary with:
        - content: AI assistant response text
        - tool_calls: List of tool calls executed (if any)
    """
    from langchain_core.messages import HumanMessage, AIMessage

    # Convert chat history to LangChain messages
    messages = []
    for msg in chat_history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))

    # Add current user message
    messages.append(HumanMessage(content=user_message))

    # Get the agent (lazy initialization)
    agent_instance = get_agent()

    # Invoke the agent
    response = agent_instance.invoke({"messages": messages})

    # Extract content and tool calls from response
    content = ""
    tool_calls = []

    if hasattr(response, 'messages') and response.messages:
        last_message = response.messages[-1]
        if hasattr(last_message, 'content'):
            content = last_message.content or ""
        if hasattr(last_message, 'tool_calls'):
            for tc in last_message.tool_calls or []:
                tool_calls.append({
                    "tool": tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", ""),
                    "args": tc.get("args") if isinstance(tc, dict) else getattr(tc, "args", {}),
                    "result": None  # Tool results are handled by the agent
                })

    return {
        "content": content,
        "tool_calls": tool_calls if tool_calls else None
    }


