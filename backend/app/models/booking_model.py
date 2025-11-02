import os

# Import calendar store functions directly
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

sys.path.insert(0, str(Path(__file__).parent.parent))
import calendar_store as cal

# Load env vars
load_dotenv()

# System prompt for the booking agent
SYSTEM_PROMPT = """You are a helpful clinical booking assistant. Your role is to help patients book appointments.

Your workflow:
1. When a patient requests a booking, first collect their information: patient name and phone number
2. Ask for the patient's name and phone number if not provided
3. When they mention "today" or "tomorrow", use the CURRENT ACTUAL DATE - today means the current date, tomorrow means current date + 1 day
4. Before creating an event, always check availability for their requested time using check_availability
5. If the slot is available, create the event using create_event with patient_name and phone_number
6. If the slot is not available, use suggest_alternative_times to find alternative slots and suggest them to the patient
7. Always be friendly, professional, and helpful
8. Confirm booking details before creating events

CRITICAL DATE HANDLING:
- When user says "today" or "tomorrow", you MUST use the actual current date (not dates from past conversations)
- "Today" = current date (use datetime.now())
- "Tomorrow" = current date + 1 day
- NEVER book appointments in the past - always validate the date is today or in the future
- Always use ISO 8601 format with timezone (e.g., "2025-01-15T14:00:00+00:00" for UTC)

Important:
- Patient name and phone number are REQUIRED - ask for them if not provided
- Default timezone is UTC if not specified by the user
- Appointment duration is typically 30 minutes unless specified
- Use 24-hour format for times
- When suggesting alternatives, provide clear options with dates and times
- Always validate that booking dates are not in the past
"""

# Define tools for the agent
@tool
def check_availability(start_iso: str, end_iso: str) -> Dict[str, Any]:
    """Check if a time slot is available for booking.

    Args:
        start_iso: Start time in ISO 8601 format (e.g., "2025-01-15T14:00:00-08:00")
        end_iso: End time in ISO 8601 format (e.g., "2025-01-15T14:30:00-08:00")

    Returns:
        Dictionary with 'available' (bool) and 'conflicts' (list) keys
    """
    try:
        result = cal.check_availability(start_iso, end_iso)
        return result
    except Exception as e:
        return {"available": False, "error": str(e), "conflicts": []}


@tool
def create_event(patient_name: str, phone_number: str, start_iso: str, end_iso: str,
                 timezone_str: str = "UTC", notes: Optional[str] = None) -> Dict[str, Any]:
    """Create a calendar event/appointment.

    Args:
        patient_name: Full name of the patient
        phone_number: Phone number of the patient
        start_iso: Start time in ISO 8601 format (e.g., "2025-01-15T14:00:00+00:00")
        end_iso: End time in ISO 8601 format (e.g., "2025-01-15T14:30:00+00:00")
        timezone_str: Timezone string (default: "UTC")
        notes: Optional notes for the appointment

    Returns:
        Dictionary with created event details
    """
    try:
        # Validate that the date is not in the past
        from datetime import datetime
        from datetime import timezone as tz

        # Parse start time and check if it's in the past
        start_dt = datetime.fromisoformat(start_iso.replace('Z', '+00:00'))
        now = datetime.now(tz.utc) if start_dt.tzinfo else datetime.now()

        # Make timezone-aware comparison
        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=tz.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=tz.utc)

        if start_dt < now:
            return {
                "success": False,
                "error": f"Cannot book appointments in the past. Requested time {start_iso} is before current time."
            }

        event_data = {
            "patient_name": patient_name,
            "phone_number": phone_number,
            "start": start_iso,
            "end": end_iso,
            "timezone": timezone_str,
            "notes": notes or "",
        }
        result = cal.create_event(event_data)
        return {"success": True, "event": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool
def suggest_alternative_times(day: str, slot_minutes: int = 30, num_slots: int = 3,
                             start_hour: int = 9, end_hour: int = 17) -> Dict[str, Any]:
    """Suggest alternative available time slots for a given day.

    Args:
        day: Date in format "YYYY-MM-DD" (e.g., "2025-01-15")
        slot_minutes: Duration of each slot in minutes (default: 30)
        num_slots: Number of suggestions to return (default: 3)
        start_hour: Start hour for searching (24-hour format, default: 9)
        end_hour: End hour for searching (24-hour format, default: 17)

    Returns:
        Dictionary with 'suggestions' list containing available time slots
    """
    try:
        # Parse the day and create time window
        day_dt = datetime.fromisoformat(day + "T00:00:00+00:00")
        slot_delta = timedelta(minutes=slot_minutes)

        # Get current time to avoid suggesting past slots
        now = datetime.now(timezone.utc)

        suggestions = []
        # Search through the day
        current = day_dt.replace(hour=start_hour, tzinfo=timezone.utc)
        end_of_day = day_dt.replace(hour=end_hour, tzinfo=timezone.utc)

        # If the day is today, start from current hour (or next hour if current hour is past)
        if day_dt.date() == now.date():
            current_hour = now.hour + (1 if now.minute > 0 else 0)
            current = day_dt.replace(hour=max(start_hour, current_hour), minute=0, tzinfo=timezone.utc)

        while current + slot_delta <= end_of_day and len(suggestions) < num_slots:
            # Skip if this slot is in the past
            if current < now:
                current += timedelta(minutes=15)
                continue

            start_iso = current.isoformat()
            end_iso = (current + slot_delta).isoformat()

            if cal.check_availability(start_iso, end_iso)["available"]:
                suggestions.append({
                    "start": start_iso,
                    "end": end_iso,
                    "duration_minutes": slot_minutes
                })
            current += timedelta(minutes=15)  # Check every 15 minutes

        return {"suggestions": suggestions, "day": day}
    except Exception as e:
        return {"suggestions": [], "error": str(e)}


# Create the agent with tools
def create_booking_agent():
    """Create a LangChain agent for booking appointments."""
    chat_model = ChatOpenAI(
        model="gpt-4o-mini",  # Using gpt-4o-mini as gpt-5-nano doesn't exist yet
        temperature=0.7,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    # Bind tools to the model
    tools = [check_availability, create_event, suggest_alternative_times]
    model_with_tools = chat_model.bind_tools(tools)

    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{user_message}")
    ])

    return prompt, model_with_tools, tools


def complete_booking_turn(chat_history: List[Dict], user_message: str) -> Dict[str, Any]:
    """Process a booking turn - handles user message and tool calls with iterative agent execution.

    Args:
        chat_history: List of previous messages in format [{"role": "user/assistant", "content": "..."}, ...]
        user_message: Current user message

    Returns:
        Dictionary with 'content' (response text) and optionally 'tool_calls' info
    """
    prompt, model, tools = create_booking_agent()

    # Get current date/time for context
    now = datetime.now(timezone.utc)
    current_date_str = now.strftime("%Y-%m-%d")
    current_time_str = now.strftime("%H:%M:%S")
    current_datetime_str = now.isoformat()
    tomorrow_date_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")

    # Enhanced system prompt with current date/time context
    enhanced_system_prompt = SYSTEM_PROMPT + f"""

CURRENT DATE AND TIME INFORMATION (use this for "today" and "tomorrow"):
- Current Date (UTC): {current_date_str}
- Current Time (UTC): {current_time_str}
- Current DateTime (ISO): {current_datetime_str}
- Today's Date: {current_date_str}
- Tomorrow's Date: {tomorrow_date_str}

IMPORTANT: When the user says "today", use {current_date_str}. When they say "tomorrow", use {tomorrow_date_str}.
Always format dates in ISO 8601 format with timezone (e.g., "2025-11-02T14:00:00+00:00").
"""

    # Convert chat history to LangChain messages
    langchain_messages = [SystemMessage(content=enhanced_system_prompt)]
    for msg in chat_history:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            langchain_messages.append(AIMessage(content=msg["content"]))

    # Add current user message
    langchain_messages.append(HumanMessage(content=user_message))

    # Agent loop: keep executing until no more tool calls
    tool_results = []
    max_iterations = 5  # Prevent infinite loops
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        # Get response from model
        response = model.invoke(langchain_messages)

        # Add AI response to messages
        langchain_messages.append(response)

        # If no tool calls, we're done
        tool_calls = getattr(response, 'tool_calls', None) or []
        if not tool_calls:
            break

        # Execute all tool calls
        from langchain_core.messages import ToolMessage
        tool_messages = []

        for tool_call in tool_calls:
            # LangChain tool calls are typically dicts with name, args, id
            if isinstance(tool_call, dict):
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("args", {})
                tool_call_id = tool_call.get("id", "")
            else:
                # Fallback for object-based tool calls
                tool_name = getattr(tool_call, "name", None)
                tool_args = getattr(tool_call, "args", {})
                tool_call_id = getattr(tool_call, "id", "")

            # Find and execute the tool
            tool_func = next((t for t in tools if t.name == tool_name), None)
            if tool_func:
                try:
                    result = tool_func.invoke(tool_args)
                    tool_results.append({
                        "tool": tool_name,
                        "args": tool_args,
                        "result": result
                    })

                    # Create tool message for model - use JSON for better parsing
                    import json
                    result_str = json.dumps(result) if isinstance(result, (dict, list)) else str(result)
                    tool_msg = ToolMessage(
                        content=result_str,
                        tool_call_id=tool_call_id
                    )
                    tool_messages.append(tool_msg)
                except Exception as e:
                    error_msg = f"Error executing {tool_name}: {str(e)}"
                    tool_results.append({
                        "tool": tool_name,
                        "args": tool_args,
                        "error": str(e)
                    })
                    tool_msg = ToolMessage(
                        content=error_msg,
                        tool_call_id=tool_call_id
                    )
                    tool_messages.append(tool_msg)

        # Add tool messages to conversation
        langchain_messages.extend(tool_messages)

    # Get final response text
    final_response = ""
    if langchain_messages:
        last_msg = langchain_messages[-1]
        if isinstance(last_msg, AIMessage):
            final_response = last_msg.content or ""

    return {
        "content": final_response,
        "tool_calls": tool_results if tool_results else None
    }
