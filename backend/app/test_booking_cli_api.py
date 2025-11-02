#!/usr/bin/env python3
"""
Terminal-based test script for the clinical booking model.
This version uses the API endpoints, so events will show up in the UI.
Make sure to run the FastAPI server first: uvicorn app.main:app --reload
"""

import sys
from pathlib import Path
from typing import Any, Dict, List

import requests

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

import json

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from models.booking_model import create_booking_agent, get_system_prompt

# API base URL
API_BASE = "http://localhost:8000"


def check_availability_via_api(start_iso: str, end_iso: str) -> Dict[str, Any]:
    """Check availability via API endpoint."""
    try:
        response = requests.post(
            f"{API_BASE}/calendar/availability/check",
            json={"start": start_iso, "end": end_iso, "timezone": "UTC"}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"available": False, "error": str(e), "conflicts": []}


def create_event_via_api(patient_name: str, phone_number: str, start_iso: str, end_iso: str,
                         timezone_str: str = "UTC",
                         notes: str = None) -> Dict[str, Any]:
    """Create event via API endpoint."""
    try:
        payload = {
            "patient_name": patient_name,
            "phone_number": phone_number,
            "start": start_iso,
            "end": end_iso,
            "timezone": timezone_str,
            "notes": notes or "",
        }
        response = requests.post(
            f"{API_BASE}/calendar/events",
            json=payload
        )
        response.raise_for_status()
        return {"success": True, "event": response.json().get("event")}
    except requests.exceptions.HTTPError as e:
        # Extract error message from response body
        error_detail = str(e)
        status_code = None
        try:
            status_code = e.response.status_code
            error_body = e.response.json()
            if "detail" in error_body:
                error_detail = error_body["detail"]
            elif isinstance(error_body, dict):
                error_detail = str(error_body)
            else:
                error_detail = str(error_body)
        except ValueError:
            # Response is not JSON
            error_detail = e.response.text if hasattr(e.response, 'text') and e.response.text else str(e)
        except Exception:
            error_detail = e.response.text if hasattr(e.response, 'text') else str(e)

        return {
            "success": False,
            "error": error_detail,
            "status_code": status_code or (e.response.status_code if hasattr(e.response, 'status_code') else None),
            "payload_sent": payload  # Include payload for debugging
        }
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


def suggest_alternative_times_via_api(day: str, slot_minutes: int = 30,
                                      num_slots: int = 3,
                                      start_hour: int = 9,
                                      end_hour: int = 17) -> Dict[str, Any]:
    """Suggest alternative times by checking API availability."""
    from datetime import datetime, timedelta, timezone

    try:
        day_dt = datetime.fromisoformat(day + "T00:00:00+00:00")
        slot_delta = timedelta(minutes=slot_minutes)

        suggestions = []
        current = day_dt.replace(hour=start_hour, tzinfo=timezone.utc)
        end_of_day = day_dt.replace(hour=end_hour, tzinfo=timezone.utc)

        while current + slot_delta <= end_of_day and len(suggestions) < num_slots:
            start_iso = current.isoformat()
            end_iso = (current + slot_delta).isoformat()

            # Check via API
            result = check_availability_via_api(start_iso, end_iso)
            if result.get("available", False):
                suggestions.append({
                    "start": start_iso,
                    "end": end_iso,
                    "duration_minutes": slot_minutes
                })
            current += timedelta(minutes=15)

        return {"suggestions": suggestions, "day": day}
    except Exception as e:
        return {"suggestions": [], "error": str(e)}


def format_tool_calls(tool_calls):
    """Format tool call information for display."""
    if not tool_calls:
        return ""

    lines = ["\n[Tool Calls Executed (via API):]"]
    for tc in tool_calls:
        tool_name = tc.get("tool", "unknown")
        args = tc.get("args", {})
        result = tc.get("result")
        error = tc.get("error")

        lines.append(f"  • {tool_name}")
        if args:
            # Highlight time-related args for create_event
            if tool_name == "create_event" and "start_iso" in args:
                start_time = args.get("start_iso", "")
                end_time = args.get("end_iso", "")
                lines.append(f"    ⏰ Start: {start_time}")
                lines.append(f"    ⏰ End: {end_time}")
                # Extract hour for verification
                try:
                    if "T" in start_time:
                        hour = start_time.split("T")[1].split(":")[0]
                        lines.append(f"    📍 Hour component: {hour}:00")
                except (IndexError, AttributeError):
                    pass
            lines.append(f"    Args: {args}")
        if error:
            lines.append(f"    ❌ Error: {error}")
        elif result:
            if isinstance(result, dict):
                if "available" in result:
                    status = "✅ Available" if result["available"] else "❌ Not Available"
                    lines.append(f"    {status}")
                elif "success" in result:
                    status = "✅ Success" if result["success"] else "❌ Failed"
                    lines.append(f"    {status}")
                    if result.get("success") and "event" in result:
                        lines.append(f"    📅 Event ID: {result['event'].get('id', 'N/A')}")
                    elif not result.get("success") and "error" in result:
                        error_msg = result["error"]
                        lines.append(f"    Error details: {error_msg}")
                        if "status_code" in result:
                            lines.append(f"    HTTP Status: {result['status_code']}")
                        if "payload_sent" in result:
                            lines.append(f"    Request payload: {result['payload_sent']}")
                elif "suggestions" in result:
                    count = len(result.get("suggestions", []))
                    lines.append(f"    Found {count} suggestion(s)")
            else:
                lines.append(f"    Result: {str(result)[:100]}")

    return "\n".join(lines)


def complete_booking_turn_api(chat_history: List[Dict], user_message: str) -> Dict[str, Any]:
    """Process booking with API integration."""
    _, model, _ = create_booking_agent()

    # Convert chat history to LangChain messages
    # Use get_system_prompt() which includes current date/time context
    langchain_messages = [SystemMessage(content=get_system_prompt())]
    for msg in chat_history:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            langchain_messages.append(AIMessage(content=msg["content"]))

    langchain_messages.append(HumanMessage(content=user_message))

    # Map tool names to API functions
    tool_map = {
        "check_availability": check_availability_via_api,
        "create_event": create_event_via_api,
        "suggest_alternative_times": suggest_alternative_times_via_api,
    }

    tool_results = []
    max_iterations = 5
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        response = model.invoke(langchain_messages)
        langchain_messages.append(response)

        tool_calls = getattr(response, 'tool_calls', None) or []
        if not tool_calls:
            break

        tool_messages = []

        for tool_call in tool_calls:
            if isinstance(tool_call, dict):
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("args", {})
                tool_call_id = tool_call.get("id", "")
            else:
                tool_name = getattr(tool_call, "name", None)
                tool_args = getattr(tool_call, "args", {})
                tool_call_id = getattr(tool_call, "id", "")

            tool_func = tool_map.get(tool_name)
            if tool_func:
                try:
                    result = tool_func(**tool_args)
                    tool_results.append({
                        "tool": tool_name,
                        "args": tool_args,
                        "result": result
                    })

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

        langchain_messages.extend(tool_messages)

    final_response = ""
    if langchain_messages:
        last_msg = langchain_messages[-1]
        if isinstance(last_msg, AIMessage):
            final_response = last_msg.content or ""

    return {
        "content": final_response,
        "tool_calls": tool_results if tool_results else None
    }


def main():
    """Main interactive loop for testing the booking agent via API."""
    print("=" * 70)
    print("🏥 Clinical Booking Assistant - Terminal Test (API Mode)")
    print("=" * 70)
    print("\n⚠️  IMPORTANT: Make sure the FastAPI server is running!")
    print("   Run: cd backend && uvicorn app.main:app --reload")
    print("\nTesting API connection...")

    # Test API connection
    try:
        response = requests.get(f"{API_BASE}/", timeout=2)
        if response.status_code == 200:
            print("✅ API server is running and accessible!")
        else:
            print(f"⚠️  API responded with status {response.status_code}")
    except requests.exceptions.RequestException:
        print(f"❌ Cannot connect to API server at {API_BASE}")
        print("   Please start the server first: uvicorn app.main:app --reload")
        return

    print("\nYou can ask for appointments naturally. Examples:")
    print("  - 'I need an appointment tomorrow at 2pm'")
    print("  - 'Can I book a slot on January 15th at 10:00 AM?'")
    print("  - 'Check if 2025-01-20 at 14:00 is available'")
    print("\nEvents created here WILL appear in the UI! 🎉")
    print("\nType 'quit' or 'exit' to end the session.\n")
    print("-" * 70)

    chat_history = []

    while True:
        try:
            user_input = input("\n👤 You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye! Have a great day!")
                break

            print("\n🤔 Processing your request...\n")
            result = complete_booking_turn_api(chat_history, user_input)

            response_text = result.get("content", "")
            tool_calls = result.get("tool_calls")

            print(f"🤖 Assistant: {response_text}")

            if tool_calls:
                print(format_tool_calls(tool_calls))

            chat_history.append({"role": "user", "content": user_input})
            chat_history.append({"role": "assistant", "content": response_text})

            print("\n" + "-" * 70)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Have a great day!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            print("\n" + "-" * 70)


if __name__ == "__main__":
    main()

