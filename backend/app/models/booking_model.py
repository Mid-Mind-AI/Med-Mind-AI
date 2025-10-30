
import json
import os
from typing import Dict, List

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
from openai import OpenAI

BOOKING_SYSTEM_PROMPT = (
    "You are Sarah, a warm and friendly clinic receptionist. "
    "Use tools to check availability, suggest alternatives, and book events. "
    "Never say something is booked until create_event succeeds. "
    "Keep replies under 2 sentences and confirm title and timezone."
)

def build_messages_with_system(history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    messages: List[Dict[str, str]] = [{"role": "system", "content": BOOKING_SYSTEM_PROMPT}]
    messages.extend(history)
    return messages

def get_openrouter_client() -> OpenAI:
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    return OpenAI(base_url=base_url, api_key=api_key)

# Tool schemas (function calling)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check if a time range is free.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start": {"type": "string", "description": "ISO 8601 with offset"},
                    "end": {"type": "string", "description": "ISO 8601 with offset"},
                    "timezone": {"type": "string"}
                },
                "required": ["start", "end", "timezone"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "suggest_times",
            "description": "Suggest free slots within a day window (UTC 9–17).",
            "parameters": {
                "type": "object",
                "properties": {
                    "day": {"type": "string", "description": "YYYY-MM-DD UTC day"},
                    "slot_minutes": {"type": "integer", "default": 30},
                    "num_slots": {"type": "integer", "default": 3}
                },
                "required": ["day"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_event",
            "description": "Create a calendar event after explicit confirmation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "start": {"type": "string", "description": "ISO 8601 with offset"},
                    "end": {"type": "string", "description": "ISO 8601 with offset"},
                    "timezone": {"type": "string"},
                    "attendees": {"type": "array", "items": {"type": "string"}, "default": []},
                    "notes": {"type": "string", "default": ""}
                },
                "required": ["title", "start", "end", "timezone"]
            }
        }
    }
]

API_BASE = os.getenv("CAL_API_BASE", "http://localhost:8000")

def http_post_json(url: str, payload: dict) -> dict:
    import requests
    r = requests.post(url, json=payload, timeout=15)
    if r.status_code >= 400:
        # Bubble up readable error to the model
        return {"error": r.text, "status": r.status_code}
    return r.json()

def run_tool(name: str, args: dict) -> dict:
    if name == "check_availability":
        return http_post_json(f"{API_BASE}/calendar/availability/check", {
            "start": args["start"],
            "end": args["end"],
            "timezone": args["timezone"],
        })

    if name == "create_event":
        return http_post_json(f"{API_BASE}/calendar/events", {
            "title": args["title"],
            "start": args["start"],
            "end": args["end"],
            "timezone": args["timezone"],
            "attendees": args.get("attendees", []),
            "notes": args.get("notes", ""),
        })

    if name == "suggest_times":
        from datetime import datetime, timedelta
        from datetime import timezone as tz
        day = datetime.fromisoformat(args["day"] + "T00:00:00+00:00")
        slot = timedelta(minutes=int(args.get("slot_minutes", 30)))
        n = int(args.get("num_slots", 3))
        t = day.replace(hour=9, tzinfo=tz.utc)
        end_of_day = day.replace(hour=17, tzinfo=tz.utc)

        suggestions = []
        while t + slot <= end_of_day and len(suggestions) < n:
            s = t.isoformat()
            e = (t + slot).isoformat()
            avail = http_post_json(f"{API_BASE}/calendar/availability/check", {
                "start": s, "end": e, "timezone": "UTC"
            })
            if avail.get("available"):
                suggestions.append({"start": s, "end": e})
            t += slot
        return {"suggestions": suggestions}

    return {"error": f"Unknown tool {name}"}

def complete_booking_turn(history: List[Dict[str, str]], user_message: str) -> Dict[str, str]:
    client = get_openrouter_client()
    full_history = history + [{"role": "user", "content": user_message}]
    messages = build_messages_with_system(full_history)

    completion = client.chat.completions.create(
        model=os.getenv("BOOKING_MODEL", "openai/gpt-5-nano"),
        messages=[{"role": m["role"], "content": m["content"]} for m in messages],
        tools=TOOLS,
        tool_choice="auto",
        temperature=0.3,
    )

    msg = completion.choices[0].message

    # Tool call loop
    while getattr(msg, "tool_calls", None):
        tool_msgs = []
        for call in msg.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments or "{}")
            result = run_tool(name, args)
            tool_msgs.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result),
            })

        messages.append({"role": "assistant", "tool_calls": msg.tool_calls})
        messages.extend(tool_msgs)

        completion = client.chat.completions.create(
            model=os.getenv("BOOKING_MODEL", "openai/gpt-5-nano"),
            messages=[{"role": m["role"], **({ "content": m["content"] } if "content" in m else { "tool_calls": m["tool_calls"]})} for m in messages],
            tools=TOOLS,
            temperature=0.3,
        )
        msg = completion.choices[0].message

    return {"role": "assistant", "content": msg.content}
