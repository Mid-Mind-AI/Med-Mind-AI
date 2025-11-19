"""Pre-visit report generation system using GPT to analyze Q&A history and create structured reports."""
import json
import os
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.agents.pre_visit_questions import get_qa_history

load_dotenv('.env.local')

DATA_DIR = Path(__file__).parent.parent / "data" / "pre_visit_data"
DATA_DIR.mkdir(exist_ok=True)

# Model configuration
MODEL_NAME = "gpt-4o-mini"
MODEL_TEMPERATURE = 0.7

# ============================================================================
# SYSTEM PROMPTS
# ============================================================================

REPORT_GENERATION_PROMPT = """# Medical Assistant - Report Generation

You are a medical assistant analyzing patient pre-visit responses to generate a comprehensive, structured report.

## Task

Based on the Q&A conversation, extract and structure the following information into a JSON format.

**IMPORTANT:** Provide detailed summaries and comprehensive information, **NOT** just one-liners or single words.

## Fields to Extract

### primary_concern
A detailed summary of the main reason for the visit, including:
- Symptoms described
- Duration of symptoms
- Severity
- Any relevant context the patient provided

**Format:** 2-4 sentences summarizing their concerns.

### medications
List of current medications, vitamins, and supplements. Each entry should include:
- Name
- Dosage
- Frequency
- Duration of use (if mentioned)

Extract **all** medication details from the conversation.

### medical_history
A comprehensive summary of the patient's medical history including:
- Chronic conditions
- Past surgeries
- Hospitalizations
- Family history
- Allergies
- Any other relevant medical information mentioned

**Format:** A detailed paragraph, **not** just "No chronic conditions."

### ai_insights
A detailed analysis (3-5 sentences) of the patient's condition based on their responses, including:
- Potential diagnoses to consider
- Red flags
- Important observations
- Recommendations for the doctor

This should be **thoughtful and comprehensive**.

### suggested_questions
A list of **5-8 specific questions** that the doctor should ask during the in-person visit based on the patient's pre-visit responses. These questions should help:
- Clarify symptoms
- Gather additional medical history
- Assess severity
- Investigate potential concerns

**Format:** Array of strings.

### notes
Any additional important information, concerns, special circumstances, or details that would be valuable for the doctor to know before the appointment. This should be a detailed summary if the patient provided substantial information.

## Output Format

Return **ONLY valid JSON**, no additional text or markdown formatting.

### Example Format

```json
{
  "primary_concern": "Patient is experiencing persistent lower back pain that started approximately 3 weeks ago after lifting heavy boxes during a move. The pain is described as a dull ache that worsens with prolonged sitting or standing, and occasionally radiates down the right leg. Patient reports difficulty sleeping on their usual side due to discomfort. They have tried over-the-counter pain relievers with minimal relief.",
  "medications": [
    {
      "name": "Ibuprofen",
      "dosage": "200mg",
      "frequency": "Twice daily",
      "duration": "Taken for the past 2 weeks for back pain"
    },
    {
      "name": "Vitamin D",
      "dosage": "1000 IU",
      "frequency": "Once daily",
      "duration": "Taken for 6 months"
    }
  ],
  "medical_history": "Patient has no known chronic conditions. They had an appendectomy in 2015 with no complications. No family history of back problems or spinal conditions. No known drug allergies. Patient is generally healthy with no other ongoing medical issues. They exercise regularly but had been inactive for 2 months prior to the move due to a busy work schedule.",
  "ai_insights": "Based on the patient's description, this appears to be a musculoskeletal issue likely related to improper lifting technique during the recent move. The radiating pain to the right leg suggests possible sciatic nerve involvement or disc-related issues. The fact that symptoms started after a specific activity (lifting) and the pain pattern worsening with prolonged positions are classic signs of mechanical back pain. However, the radiation to the leg warrants further investigation to rule out disc herniation. The patient would benefit from a physical examination, assessment of range of motion, and possibly imaging if symptoms persist or worsen. Early intervention with proper rest, physical therapy, and potentially prescription anti-inflammatories may prevent chronic issues.",
  "suggested_questions": [
    "Can you describe the exact location of the pain and if it has moved or changed since it started?",
    "On a scale of 1-10, what is the current pain level, and what was it at its worst?",
    "Have you noticed any numbness, tingling, or weakness in your legs or feet?",
    "What activities or positions make the pain better or worse?",
    "Have you tried any specific exercises or stretches, and if so, what was the effect?",
    "Are there any red flags such as loss of bowel or bladder control, or pain that wakes you up at night?",
    "How has this pain impacted your daily activities and work?",
    "What is your typical lifting technique, and do you engage in heavy lifting regularly?"
  ],
  "notes": "Patient mentioned they have an important presentation next week and is concerned about being able to sit for extended periods. They are also planning a family vacation in 3 weeks and are worried about travel. Patient prefers conservative treatment approaches if possible. They have not seen a doctor for this issue yet."
}
```"""


# ============================================================================
# REPORT GENERATION
# ============================================================================

def generate_pre_visit_report(event_id: str, patient_name: str, doctor_name: str, appointment_datetime: str) -> Dict:
    """Generate a pre-visit report JSON from Q&A history using GPT."""
    qa_history = get_qa_history(event_id)

    if not qa_history:
        return {
            "primary_concern": None,
            "medications": [],
            "medical_history": None,
            "ai_insights": None,
            "suggested_questions": [],
            "notes": None
        }

    model = ChatOpenAI(
        model=MODEL_NAME,
        temperature=MODEL_TEMPERATURE,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # Build conversation context from Q&A history
    qa_text = "\n".join([
        f"Q: {qa['question']}\nA: {qa['answer']}"
        for qa in qa_history
    ])

    messages = [
        SystemMessage(content=REPORT_GENERATION_PROMPT),
        HumanMessage(content=f"Patient: {patient_name}\nDoctor: {doctor_name}\nAppointment: {appointment_datetime}\n\nQ&A History:\n{qa_text}")
    ]

    response = model.invoke(messages)
    report_text = response.content.strip()

    # Try to extract JSON from response (in case model wraps it)
    if "```json" in report_text:
        report_text = report_text.split("```json")[1].split("```")[0].strip()
    elif "```" in report_text:
        report_text = report_text.split("```")[1].split("```")[0].strip()

    report = json.loads(report_text)

    # Validate and ensure all required fields exist
    return {
        "primary_concern": report.get("primary_concern"),
        "medications": report.get("medications", []),
        "medical_history": report.get("medical_history"),
        "ai_insights": report.get("ai_insights"),
        "suggested_questions": report.get("suggested_questions", []),
        "notes": report.get("notes")
    }


# ============================================================================
# REPORT DATA MANAGEMENT
# ============================================================================

def save_report(event_id: str, report: Dict):
    """Save the generated report to the event's data file."""
    file_path = DATA_DIR / f"{event_id}.json"

    if file_path.exists():
        with open(file_path, 'r') as f:
            data = json.load(f)
    else:
        data = {"qa": [], "event_id": event_id}

    data["report"] = report

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def get_report(event_id: str) -> Optional[Dict]:
    """Get the saved report for an event."""
    file_path = DATA_DIR / f"{event_id}.json"

    if not file_path.exists():
        return None

    with open(file_path, 'r') as f:
        data = json.load(f)
        return data.get("report")

