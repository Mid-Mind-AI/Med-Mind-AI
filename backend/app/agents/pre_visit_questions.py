"""Pre-visit questions system using GPT to generate dynamic questions."""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

load_dotenv('.env.local')

DATA_DIR = Path(__file__).parent.parent / "data" / "pre_visit_data"
DATA_DIR.mkdir(exist_ok=True)

# Model configuration
MODEL_NAME = "gpt-4o-mini"
MODEL_TEMPERATURE = 0.7

# ============================================================================
# SYSTEM PROMPTS
# ============================================================================

QUESTION_GENERATION_PROMPT = """# Medical Assistant - Question Generation

You are a helpful medical assistant collecting pre-visit information from patients.

## IMPORTANT First Interaction Rules

If this is the very first interaction (no questions asked yet), you **MUST** first ask:
> "Before you leave, I would like to ask you a few questions as to why you are visiting today. Would you like to continue?"

If they say yes, then proceed with the first actual question:
> "Could you tell me the main reason for your visit today?"

## Question Guidelines

For subsequent questions, ask **ONE** relevant follow-up question based on the patient's previous responses.

The question should be:
- **Natural and conversational** - Use friendly, patient-friendly language
- **Medically relevant** - Focus on gathering useful clinical information
- **Not repetitive** - Don't ask about things already covered
- **Focused** - Gather information that would be valuable for the doctor

## Response Format

Keep your response to **just the question itself**, no additional text or commentary."""


FIRST_QUESTION_INSTRUCTION = "This is the first interaction. Ask the consent question first, then if they say yes, ask why they are visiting today."


# ============================================================================
# DATA MANAGEMENT FUNCTIONS
# ============================================================================

def save_qa(event_id: str, question: str, answer: str):
    """Save Q&A pair to event's data file."""
    file_path = DATA_DIR / f"{event_id}.json"

    if file_path.exists():
        with open(file_path, 'r') as f:
            data = json.load(f)
    else:
        data = {"qa": [], "event_id": event_id}

    data["qa"].append({"question": question, "answer": answer})

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def get_qa_history(event_id: str) -> List[Dict]:
    """Get all Q&A pairs for an event."""
    file_path = DATA_DIR / f"{event_id}.json"

    if not file_path.exists():
        return []

    with open(file_path, 'r') as f:
        data = json.load(f)
        return data.get("qa", [])


# ============================================================================
# QUESTION GENERATION
# ============================================================================

def generate_next_question(event_id: str) -> Optional[str]:
    """Generate the next question based on previous Q&A history using GPT."""
    qa_history = get_qa_history(event_id)

    if len(qa_history) >= 7:
        return None  # Already asked 7 questions

    model = ChatOpenAI(
        model=MODEL_NAME,
        temperature=MODEL_TEMPERATURE,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # Build conversation context
    messages = [SystemMessage(content=QUESTION_GENERATION_PROMPT)]

    # Add Q&A history
    for qa in qa_history:
        messages.append(HumanMessage(content=f"Q: {qa['question']}\nA: {qa['answer']}"))

    # If this is the first question, ask the consent question first
    if len(qa_history) == 0:
        messages.append(HumanMessage(content=FIRST_QUESTION_INSTRUCTION))

    try:
        response = model.invoke(messages)
        question = response.content.strip()
        return question
    except Exception:
        # Return None if GPT API fails
        return None

