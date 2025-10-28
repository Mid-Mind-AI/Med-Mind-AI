import os
from typing import Dict, List

from openai import OpenAI

API_KEY = "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"

BOOKING_SYSTEM_PROMPT = (
    "You are Sarah, a warm and friendly front desk receptionist at MedCare Clinic. "
    "Your job is to help patients schedule appointments by collecting their preferred times. "
    "Speak naturally and conversationally, like you're talking to someone in person. "
    "Use contractions (I'd, we'll, etc.) and friendly phrases. "
    "Ask for their preferred days, time of day (morning/afternoon/evening), and timezone. "
    "If they've already shared some details, acknowledge what they said and ask for the remaining info. "
    "Keep responses conversational and under 2 sentences. "
    "Never claim to have actually booked anything - just collect preferences. "
    "Remember: you're preparing for text-to-speech, so write as you would speak."
)


def build_messages_with_system(history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Build messages list with system prompt prepended."""
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": BOOKING_SYSTEM_PROMPT}
    ]
    messages.extend(history)
    return messages


def get_openrouter_client() -> OpenAI:
    """Get OpenAI client configured for OpenRouter."""
    api_key = os.getenv("OPENROUTER_API_KEY", API_KEY)
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    return OpenAI(base_url=base_url, api_key=api_key)


def complete_booking_turn(history: List[Dict[str, str]], user_message: str) -> Dict[str, str]:
    """
    Given prior history and a new user message, call the booking model and return assistant reply.

    Args:
        history: List of previous messages in the conversation
        user_message: The current user message

    Returns:
        Dict with role "assistant" and content from model response
    """
    client = get_openrouter_client()
    full_history = history + [{"role": "user", "content": user_message}]
    messages = build_messages_with_system(full_history)

    completion = client.chat.completions.create(
        model=os.getenv("BOOKING_MODEL", "openai/gpt-5-nano"),
        messages=[
            # OpenRouter supports OpenAI's chat format; we pass simple role/content pairs
            {"role": m["role"], "content": m["content"]} for m in messages
        ],
        temperature=0.3,
    )

    content = completion.choices[0].message.content
    return {"role": "assistant", "content": content}
