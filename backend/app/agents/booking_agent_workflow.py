"""Unified workflow orchestrator for booking and pre-visit agents.

This module provides a clean, simple API for the frontend to interact with
all the AI agents and models in the system. It combines:
- Booking agent (conversational appointment booking)
- Pre-visit questions agent (dynamic Q&A generation)
- Pre-visit report generation (AI-generated medical reports)

All agents work together seamlessly through this workflow.
"""

from typing import Any, Dict, List

from app.models.booking_model import complete_booking_turn
from app.models.pre_visit_questions import (
    generate_next_question,
    get_qa_history,
    save_qa,
)
from app.models.pre_visit_report import (
    generate_pre_visit_report as generate_report,
)
from app.models.pre_visit_report import (
    get_report,
    save_report,
)
from app.services import calendar_store as cal

# ============================================================================
# WORKFLOW STATE MANAGEMENT
# ============================================================================

def get_workflow_state(event_id: str) -> Dict[str, Any]:
    """Get the current state of the workflow for an event.

    Args:
        event_id: The event ID to check

    Returns:
        Dictionary with workflow state including:
        - event_exists: Whether the event exists
        - questions_completed: Number of questions answered (0-7)
        - is_questions_complete: Whether all 7 questions are done
        - report_exists: Whether a report has been generated
        - event: Event details if exists
        - report: Report data if exists
    """
    event = cal.get_event_by_id(event_id)
    qa_history = get_qa_history(event_id)
    report = get_report(event_id)

    return {
        "event_exists": event is not None,
        "questions_completed": len(qa_history),
        "is_questions_complete": len(qa_history) >= 7,
        "report_exists": report is not None,
        "event": event,
        "report": report,
        "qa_history": qa_history,
    }


# ============================================================================
# BOOKING WORKFLOW
# ============================================================================

def process_booking_message(
    chat_history: List[Dict[str, str]],
    user_message: str,
) -> Dict[str, Any]:
    """Process a booking message through the booking agent.

    This handles the conversational booking flow where users can:
    - Ask about availability
    - Request appointments
    - Get time suggestions

    Args:
        chat_history: Previous messages in format [{"role": "user/assistant", "content": "..."}]
        user_message: Current user message

    Returns:
        Dictionary with:
        - content: AI assistant response text
        - tool_calls: List of tool calls executed (if any)
        - event_created: Event details if an event was created (None otherwise)

    Example:
        >>> result = process_booking_message([], "I need an appointment tomorrow at 2pm")
        >>> print(result["content"])
        >>> if result["event_created"]:
        ...     event_id = result["event_created"]["id"]
        ...     # Start pre-visit questions with this event_id
    """
    # Process through booking agent
    result = complete_booking_turn(chat_history, user_message)

    # Check if an event was created
    event_created = None
    if result.get("tool_calls"):
        for tool_call in result["tool_calls"]:
            if tool_call.get("tool") == "create_event":
                tool_result = tool_call.get("result", {})
                if tool_result.get("success") and tool_result.get("event"):
                    event_created = tool_result["event"]
                    break

    return {
        "content": result.get("content", ""),
        "tool_calls": result.get("tool_calls"),
        "event_created": event_created,
    }


# ============================================================================
# PRE-VISIT QUESTIONS WORKFLOW
# ============================================================================

def get_next_pre_visit_question(event_id: str) -> Dict[str, Any]:
    """Get the next pre-visit question for an event.

    This will automatically generate the next question based on:
    - Previous Q&A history
    - Patient responses so far

    Args:
        event_id: The event ID to get the question for

    Returns:
        Dictionary with:
        - question: The next question to ask (None if complete)
        - question_count: Number of questions asked so far
        - is_complete: Whether all 7 questions have been answered
        - message: Optional status message

    Example:
        >>> result = get_next_pre_visit_question("event-123")
        >>> if result["question"]:
        ...     print(f"Question {result['question_count']}: {result['question']}")
        ... else:
        ...     print("All questions complete!")
    """
    # Verify event exists
    event = cal.get_event_by_id(event_id)
    if not event:
        return {
            "question": None,
            "question_count": 0,
            "is_complete": True,
            "message": "Event not found",
        }

    # Get current Q&A history
    qa_history = get_qa_history(event_id)

    # Check if already complete
    if len(qa_history) >= 7:
        return {
            "question": None,
            "question_count": len(qa_history),
            "is_complete": True,
            "message": "All questions have been answered.",
        }

    # Generate next question
    question = generate_next_question(event_id)

    if not question:
        return {
            "question": None,
            "question_count": len(qa_history),
            "is_complete": True,
            "message": "All questions have been answered.",
        }

    return {
        "question": question,
        "question_count": len(qa_history),
        "is_complete": False,
    }


def submit_pre_visit_answer(
    event_id: str,
    question: str,
    answer: str,
) -> Dict[str, Any]:
    """Submit an answer to a pre-visit question.

    Args:
        event_id: The event ID
        question: The question that was asked
        answer: The patient's answer

    Returns:
        Dictionary with:
        - status: "success" or "error"
        - question_count: Updated question count
        - is_complete: Whether all 7 questions are done
        - next_question: The next question (if any)
        - message: Optional status message

    Example:
        >>> result = submit_pre_visit_answer("event-123", "Why are you visiting?", "Back pain")
        >>> if result["is_complete"]:
        ...     # Generate report
        ... else:
        ...     print(f"Next: {result['next_question']}")
    """
    # Verify event exists
    event = cal.get_event_by_id(event_id)
    if not event:
        return {
            "status": "error",
            "message": "Event not found",
            "question_count": 0,
            "is_complete": False,
            "next_question": None,
        }

    # Save the Q&A
    save_qa(event_id, question, answer)

    # Get updated history
    qa_history = get_qa_history(event_id)

    # Check if complete
    if len(qa_history) >= 7:
        return {
            "status": "success",
            "question_count": len(qa_history),
            "is_complete": True,
            "next_question": None,
            "message": "All questions completed. You can now generate the report.",
        }

    # Get next question
    next_question = generate_next_question(event_id)

    return {
        "status": "success",
        "question_count": len(qa_history),
        "is_complete": False,
        "next_question": next_question,
    }


# ============================================================================
# PRE-VISIT REPORT WORKFLOW
# ============================================================================

def generate_pre_visit_report(event_id: str) -> Dict[str, Any]:
    """Generate a pre-visit report from Q&A history.

    This should be called after all 7 pre-visit questions have been answered.
    The report will be automatically saved and linked to the event.

    Args:
        event_id: The event ID to generate the report for

    Returns:
        Dictionary with:
        - status: "success" or "error"
        - report: The generated report (if successful)
        - message: Status message

    Example:
        >>> result = generate_pre_visit_report("event-123")
        >>> if result["status"] == "success":
        ...     report = result["report"]
        ...     print(f"Primary concern: {report['primary_concern']}")
    """
    # Verify event exists
    event = cal.get_event_by_id(event_id)
    if not event:
        return {
            "status": "error",
            "report": None,
            "message": "Event not found",
        }

    # Check if questions are complete
    qa_history = get_qa_history(event_id)
    if len(qa_history) < 7:
        return {
            "status": "error",
            "report": None,
            "message": f"Not all questions answered. {len(qa_history)}/7 completed.",
        }

    try:
        # Generate report
        report = generate_report(
            event_id=event_id,
            patient_name=event["patient_name"],
            doctor_name=event["doctor_name"],
            appointment_datetime=event["start"],
        )

        # Save report
        save_report(event_id, report)

        return {
            "status": "success",
            "report": report,
            "message": "Report generated successfully",
        }
    except Exception as e:
        return {
            "status": "error",
            "report": None,
            "message": f"Failed to generate report: {str(e)}",
        }


