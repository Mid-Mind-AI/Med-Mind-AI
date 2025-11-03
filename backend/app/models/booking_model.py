import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import calendar_store as cal
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

# Add parent directory to path for calendar_store import
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()



# Model
MODEL_NAME = "gpt-4o-mini"
MODEL_TEMPERATURE = 0.7

# Agent configuration
MAX_ITERATIONS = 5  # Prevent infinite loops in agent execution

# Timezone configuration
USER_TIMEZONE_OFFSET_HOURS = 5  # Eastern Time is UTC-5
DEFAULT_TIMEZONE = "UTC"

# Appointment defaults
DEFAULT_APPOINTMENT_DURATION_MINUTES = 30
DEFAULT_START_HOUR = 9
DEFAULT_END_HOUR = 17
DEFAULT_NUM_SLOTS = 3
SLOT_CHECK_INTERVAL_MINUTES = 15


# ============================================================================
# DATE/TIME UTILITIES
# ============================================================================

def parse_iso_datetime(iso_string: str) -> datetime:
    """Parse an ISO 8601 datetime string, handling 'Z' suffix.

    Args:
        iso_string: ISO 8601 datetime string

    Returns:
        Parsed datetime object
    """
    # Handle 'Z' suffix (UTC) by converting to +00:00
    if iso_string.endswith('Z'):
        iso_string = iso_string[:-1] + '+00:00'
    return datetime.fromisoformat(iso_string)


def validate_not_in_past(start_iso: str) -> Optional[str]:
    """Validate that a datetime is not in the past.

    Args:
        start_iso: ISO 8601 datetime string

    Returns:
        Error message if invalid, None if valid
    """
    start_dt = parse_iso_datetime(start_iso)
    now = datetime.now(timezone.utc)

    # Ensure both are timezone-aware
    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=timezone.utc)

    if start_dt < now:
        return f"Cannot book appointments in the past. Requested time {start_iso} is before current time."
    return None


# ============================================================================
# SYSTEM PROMPT GENERATION
# ============================================================================

SYSTEM_PROMPT_TEMPLATE = """You are a helpful clinical booking assistant. Your role is to help patients book appointments.

## Communication Style

You are speaking with patients as if you are a front desk clinical assistant. Communicate naturally and conversationally:
- Use complete sentences and natural speech patterns
- Do NOT use bullet points, numbered lists, or formatted lists in your responses
- Speak as a friendly, professional person would in person or on the phone
- Present information in flowing sentences, not structured lists
- When offering multiple time options, state them naturally (e.g., "We have availability tomorrow at 2 PM, or on Thursday at 10 AM, or Friday afternoon at 3 PM")
- Keep responses warm, professional, and human-like

## Your Workflow

1. When a patient requests a booking, first collect their information: patient name, phone number, and which doctor they are visiting
2. Ask for the patient's name, phone number, and doctor name if not provided
3. When they mention "today" or "tomorrow", use the CURRENT ACTUAL DATE - today means the current date, tomorrow means current date + 1 day
4. Before creating an event, always check availability for their requested time using `check_availability`
5. If the slot is available, create the event using `create_event` with `patient_name`, `phone_number`, and `doctor_name`
6. If the slot is not available, use `suggest_alternative_times` to find alternative slots and suggest them to the patient
7. Always be friendly, professional, and helpful
8. Confirm booking details before creating events

## Critical Date and Time Handling

### Date Handling

- When user says "today" or "tomorrow", you MUST use the actual current date (not dates from past conversations)
- "Today" = current date (use `datetime.now()`)
- "Tomorrow" = current date + 1 day
- NEVER book appointments in the past - always validate the date is today or in the future
- Always use ISO 8601 format with timezone (e.g., `"2025-01-15T14:00:00+00:00"` for UTC)

### Current Date and Time Information

Use this for "today" and "tomorrow":
- Current Date (UTC): `{current_date_str}`
- Current Time (UTC): `{current_time_str}`
- Current DateTime (ISO): `{current_datetime_str}`
- Today's Date: `{current_date_str}`
- Tomorrow's Date: `{tomorrow_date_str}`

**Important:**
- When the user says "today", use `{current_date_str}`. When they say "tomorrow", use `{tomorrow_date_str}`.
- Always format dates in ISO 8601 format with timezone (e.g., `"2025-11-02T20:00:00+00:00"`).

### Time Zone Handling

- **IMPORTANT:** When users specify a time like "3 PM", they almost always mean 3 PM in THEIR LOCAL TIMEZONE, NOT UTC
- The user's local timezone is approximately UTC-`{USER_TIMEZONE_OFFSET_HOURS}` (Eastern Time)
- When user says "3 PM", they mean 3 PM local time, which should be converted to UTC before storing
- **TIMEZONE CONVERSION:** The user is in approximately UTC-`{USER_TIMEZONE_OFFSET_HOURS}` (Eastern Time). When they say a time, ADD `{USER_TIMEZONE_OFFSET_HOURS}` HOURS to convert to UTC:
  - "3 PM" local = 20:00 UTC (15:00 + `{USER_TIMEZONE_OFFSET_HOURS}` = 20:00)
  - "2 PM" local = 19:00 UTC (14:00 + `{USER_TIMEZONE_OFFSET_HOURS}` = 19:00)
  - "10 AM" local = 15:00 UTC (10:00 + `{USER_TIMEZONE_OFFSET_HOURS}` = 15:00)
  - "10 PM" local = 03:00 UTC next day (22:00 + `{USER_TIMEZONE_OFFSET_HOURS}` = 27:00 - 24 = 03:00 next day)
- **CRITICAL:** If user says "3 PM", you MUST use 20:00 UTC (not 15:00 UTC), so it displays correctly as 3 PM in their timezone
- Always use 24-hour format (00:00 to 23:59) when creating ISO 8601 timestamps
- When user provides a time, assume it's in their local timezone (approximately UTC-`{USER_TIMEZONE_OFFSET_HOURS}`) and add `{USER_TIMEZONE_OFFSET_HOURS}` hours to convert to UTC
- **Example:** If user wants appointment "tomorrow at 3 PM", and they're in UTC-`{USER_TIMEZONE_OFFSET_HOURS}`:
  - 3 PM local = 15:00 EST
  - Convert to UTC: 15:00 + `{USER_TIMEZONE_OFFSET_HOURS}` hours = 20:00 UTC
  - Create timestamp: `"2025-11-02T20:00:00+00:00"` (this will display as 3 PM local time)

## Additional Guidelines

- Patient name, phone number, and doctor name are REQUIRED - ask for them if not provided
- Always ask which doctor the patient is visiting when collecting booking information
- Default timezone is `{DEFAULT_TIMEZONE}` if not specified by the user
- Appointment duration is typically `{DEFAULT_APPOINTMENT_DURATION_MINUTES}` minutes unless specified
- Use 24-hour format for times in ISO timestamps
- When suggesting alternatives, provide clear options with dates and times
- Always validate that booking dates are not in the past
"""


def get_system_prompt() -> str:
    """Format the system prompt template with current date/time information.

    Returns:
        Formatted system prompt string with dynamic date/time context
    """
    # Get current date/time for context
    now = datetime.now(timezone.utc)
    current_date_str = now.strftime("%Y-%m-%d")
    current_time_str = now.strftime("%H:%M:%S")
    current_datetime_str = now.isoformat()
    tomorrow_date_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")

    return SYSTEM_PROMPT_TEMPLATE.format(
        current_date_str=current_date_str,
        current_time_str=current_time_str,
        current_datetime_str=current_datetime_str,
        tomorrow_date_str=tomorrow_date_str,
        USER_TIMEZONE_OFFSET_HOURS=USER_TIMEZONE_OFFSET_HOURS,
        DEFAULT_TIMEZONE=DEFAULT_TIMEZONE,
        DEFAULT_APPOINTMENT_DURATION_MINUTES=DEFAULT_APPOINTMENT_DURATION_MINUTES
    )






# ============================================================================
# TOOLS
# ============================================================================

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
def create_event(patient_name: str, phone_number: str, doctor_name: str, start_iso: str, end_iso: str,
                 timezone_str: str = DEFAULT_TIMEZONE, notes: Optional[str] = None) -> Dict[str, Any]:
    """Create a calendar event/appointment.

    Args:
        patient_name: Full name of the patient
        phone_number: Phone number of the patient
        doctor_name: Name of the doctor the patient is visiting
        start_iso: Start time in ISO 8601 format (e.g., "2025-01-15T14:00:00+00:00")
        end_iso: End time in ISO 8601 format (e.g., "2025-01-15T14:30:00+00:00")
        timezone_str: Timezone string (default: "UTC")
        notes: Optional notes for the appointment

    Returns:
        Dictionary with created event details
    """
    try:
        # Validate that the date is not in the past
        validation_error = validate_not_in_past(start_iso)
        if validation_error:
            return {"success": False, "error": validation_error}

        event_data = {
            "patient_name": patient_name,
            "phone_number": phone_number,
            "doctor_name": doctor_name,
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
def suggest_alternative_times(day: str, slot_minutes: int = DEFAULT_APPOINTMENT_DURATION_MINUTES,
                             num_slots: int = DEFAULT_NUM_SLOTS,
                             start_hour: int = DEFAULT_START_HOUR,
                             end_hour: int = DEFAULT_END_HOUR) -> Dict[str, Any]:
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

        now = datetime.now(timezone.utc)

        suggestions = []

        current = day_dt.replace(hour=start_hour, tzinfo=timezone.utc)
        end_of_day = day_dt.replace(hour=end_hour, tzinfo=timezone.utc)

        if day_dt.date() == now.date():
            current_hour = now.hour + (1 if now.minute > 0 else 0)
            current = day_dt.replace(hour=max(start_hour, current_hour), minute=0, tzinfo=timezone.utc)

        while current + slot_delta <= end_of_day and len(suggestions) < num_slots:
            # Skip if this slot is in the past
            if current < now:
                current += timedelta(minutes=SLOT_CHECK_INTERVAL_MINUTES)
                continue

            start_iso = current.isoformat()
            end_iso = (current + slot_delta).isoformat()

            if cal.check_availability(start_iso, end_iso)["available"]:
                suggestions.append({
                    "start": start_iso,
                    "end": end_iso,
                    "duration_minutes": slot_minutes
                })
            current += timedelta(minutes=SLOT_CHECK_INTERVAL_MINUTES)

        return {"suggestions": suggestions, "day": day}
    except Exception as e:
        return {"suggestions": [], "error": str(e)}


# ============================================================================
# AGENT CREATION
# ============================================================================

def create_booking_agent():
    """Create a LangChain ReAct agent for booking appointments.

    Returns:
        LangChain agent instance configured with model, tools, and system prompt
    """
    model = ChatOpenAI(
        model=MODEL_NAME,
        temperature=MODEL_TEMPERATURE,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    tools = [check_availability, create_event, suggest_alternative_times]

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=get_system_prompt()
    )

    return agent


def get_model_and_tools():
    """Get model with tools bound and tools list for backward compatibility.

    This is useful for code that needs to manually execute tools (e.g., API-based execution).

    Returns:
        Tuple of (model_with_tools, tools_list)
    """
    model = ChatOpenAI(
        model=MODEL_NAME,
        temperature=MODEL_TEMPERATURE,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    tools = [check_availability, create_event, suggest_alternative_times]
    model_with_tools = model.bind_tools(tools)

    return model_with_tools, tools


def complete_booking_turn(chat_history: List[Dict], user_message: str) -> Dict[str, Any]:
    """Process a booking turn using LangChain ReAct agent.

    Args:
        chat_history: List of previous messages in format [{"role": "user/assistant", "content": "..."}, ...]
        user_message: Current user message

    Returns:
        Dictionary with 'content' (response text) and optionally 'tool_calls' info
    """
    agent = create_booking_agent()

    # Convert chat history to LangChain messages
    langchain_messages = []
    for msg in chat_history:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            langchain_messages.append(AIMessage(content=msg["content"]))

    # Add current user message
    langchain_messages.append(HumanMessage(content=user_message))

    # Invoke agent - it handles tool calls automatically via ReAct pattern
    response = agent.invoke({"messages": langchain_messages})

    # Extract final response from the messages
    messages = response.get("messages", [])
    final_response = ""
    if messages:
        last_msg = messages[-1]
        if hasattr(last_msg, 'content'):
            final_response = last_msg.content or ""
        elif isinstance(last_msg, dict):
            final_response = last_msg.get("content", "")

    return {
        "content": final_response,
        "tool_calls": None  # ReAct agent handles this internally
    }

# ============================================================================
# MESSAGE CONVERSION UTILITIES
# ============================================================================

def convert_chat_history_to_langchain(chat_history: List[Dict]) -> List:
    """Convert chat history from API format to LangChain message format.

    Args:
        chat_history: List of messages in format [{"role": "user/assistant", "content": "..."}, ...]

    Returns:
        List of LangChain message objects
    """
    langchain_messages = [SystemMessage(content=get_system_prompt())]

    for msg in chat_history:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            langchain_messages.append(AIMessage(content=msg["content"]))

    return langchain_messages


def extract_tool_call_info(tool_call: Any) -> Tuple[Optional[str], Dict, str]:
    """Extract tool name, args, and call ID from a tool call object.

    Args:
        tool_call: Tool call object (dict or object with attributes)

    Returns:
        Tuple of (tool_name, tool_args, tool_call_id)
    """
    if isinstance(tool_call, dict):
        return (
            tool_call.get("name"),
            tool_call.get("args", {}),
            tool_call.get("id", "")
        )
    else:
        # Fallback for object-based tool calls
        return (
            getattr(tool_call, "name", None),
            getattr(tool_call, "args", {}),
            getattr(tool_call, "id", "")
        )


# ============================================================================
# TOOL EXECUTION
# ============================================================================

def execute_tool_calls(tool_calls: List[Any], tools: List) -> Tuple[List, List]:
    """Execute tool calls and return results and tool messages.

    Args:
        tool_calls: List of tool call objects to execute
        tools: List of available tool functions

    Returns:
        Tuple of (tool_results, tool_messages)
    """
    tool_results = []
    tool_messages = []

    for tool_call in tool_calls:
        tool_name, tool_args, tool_call_id = extract_tool_call_info(tool_call)

        # Find and execute the tool
        tool_func = next((t for t in tools if t.name == tool_name), None)
        if not tool_func:
            continue

        try:
            result = tool_func.invoke(tool_args)
            tool_results.append({
                "tool": tool_name,
                "args": tool_args,
                "result": result
            })

            # Create tool message for model
            result_str = json.dumps(result) if isinstance(result, (dict, list)) else str(result)
            tool_msg = ToolMessage(content=result_str, tool_call_id=tool_call_id)
            tool_messages.append(tool_msg)

        except Exception as e:
            error_msg = f"Error executing {tool_name}: {str(e)}"
            tool_results.append({
                "tool": tool_name,
                "args": tool_args,
                "error": str(e)
            })
            tool_msg = ToolMessage(content=error_msg, tool_call_id=tool_call_id)
            tool_messages.append(tool_msg)

    return tool_results, tool_messages


