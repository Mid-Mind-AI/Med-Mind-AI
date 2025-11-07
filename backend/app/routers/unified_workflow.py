"""Simplified unified workflow endpoint for frontend integration.

This provides a single, simple endpoint that handles the entire flow:
Booking → Questions → Report
"""

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.booking_agent_workflow import (
    generate_pre_visit_report,
    get_next_pre_visit_question,
    get_workflow_state,
    process_booking_message,
    submit_pre_visit_answer,
)

router = APIRouter(prefix="/workflow", tags=["Workflow"])

class WorkflowRequest(BaseModel):
    """Unified workflow request - handles booking, questions, and reports."""
    # For booking
    user_message: Optional[str] = Field(None, description="User message for booking")
    chat_history: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Previous conversation history"
    )

    # For questions (if event_id provided)
    event_id: Optional[str] = Field(None, description="Event ID (if already have one)")
    answer: Optional[str] = Field(None, description="Answer to current question (if answering)")
    question: Optional[str] = Field(None, description="The question being answered")

    # For report generation
    generate_report: bool = Field(False, description="Set to true to generate report after questions")


# ============================================================================
# UNIFIED WORKFLOW ENDPOINT
# ============================================================================

@router.post("/process")
async def process_workflow(request: WorkflowRequest) -> Dict:
    """Unified workflow endpoint - handles booking, questions, and reports.

    This endpoint intelligently handles the entire flow:

    1. **If user_message provided** → Process booking
    2. **If event_id provided** → Get next question or submit answer
    3. **If generate_report=true** → Generate report

    Returns the current state and what to do next.

    Example Flow:
    ```
    # Step 1: Book appointment
    POST /workflow/process
    { "user_message": "I need appointment tomorrow at 2pm" }
    → Returns: { "event_id": "...", "next_question": "...", "status": "booking_complete" }

    # Step 2: Answer questions (repeat 7 times)
    POST /workflow/process
    { "event_id": "...", "answer": "Back pain", "question": "Why are you visiting?" }
    → Returns: { "next_question": "...", "question_count": 1, "status": "answering_questions" }

    # Step 3: Generate report
    POST /workflow/process
    { "event_id": "...", "generate_report": true }
    → Returns: { "report": {...}, "status": "report_generated" }
    ```
    """
    try:
        # Step 1: Handle booking
        if request.user_message:
            booking_result = process_booking_message(
                chat_history=request.chat_history,
                user_message=request.user_message
            )

            if booking_result.get("event_created"):
                event_id = booking_result["event_created"]["id"]

                # Automatically get first question after booking
                question_result = get_next_pre_visit_question(event_id)

                return {
                    "status": "booking_complete",
                    "message": booking_result["content"],
                    "event_id": event_id,
                    "event": booking_result["event_created"],
                    "next_question": question_result.get("question"),
                    "question_count": question_result.get("question_count", 0),
                    "is_questions_complete": question_result.get("is_complete", False)
                }
            else:
                return {
                    "status": "booking_in_progress",
                    "message": booking_result["content"],
                    "event_id": None
                }

        # Step 2: Handle questions (if event_id provided)
        if request.event_id:
            # Submit answer if provided
            if request.answer and request.question:
                answer_result = submit_pre_visit_answer(
                    event_id=request.event_id,
                    question=request.question,
                    answer=request.answer
                )

                if answer_result["is_complete"]:
                    # All questions done - check if should generate report
                    if request.generate_report:
                        report_result = generate_pre_visit_report(request.event_id)
                        if report_result["status"] == "success":
                            return {
                                "status": "report_generated",
                                "event_id": request.event_id,
                                "report": report_result["report"],
                                "question_count": 7,
                                "is_questions_complete": True
                            }

                    return {
                        "status": "questions_complete",
                        "event_id": request.event_id,
                        "question_count": 7,
                        "is_questions_complete": True,
                        "message": "All questions completed. Ready to generate report."
                    }
                else:
                    # Get next question
                    question_result = get_next_pre_visit_question(request.event_id)
                    return {
                        "status": "answering_questions",
                        "event_id": request.event_id,
                        "next_question": question_result.get("question"),
                        "question_count": answer_result["question_count"],
                        "is_questions_complete": False
                    }

            # Just get next question (no answer provided)
            elif request.generate_report:
                # Generate report
                report_result = generate_pre_visit_report(request.event_id)
                if report_result["status"] == "success":
                    return {
                        "status": "report_generated",
                        "event_id": request.event_id,
                        "report": report_result["report"]
                    }
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=report_result.get("message", "Failed to generate report")
                    )
            else:
                # Get current question
                question_result = get_next_pre_visit_question(request.event_id)
                state = get_workflow_state(request.event_id)

                return {
                    "status": "question_ready",
                    "event_id": request.event_id,
                    "next_question": question_result.get("question"),
                    "question_count": question_result.get("question_count", 0),
                    "is_questions_complete": question_result.get("is_complete", False),
                    "report_exists": state.get("report_exists", False),
                    "workflow_state": state
                }

        # No action specified
        raise HTTPException(
            status_code=400,
            detail="Must provide either user_message (for booking) or event_id (for questions)"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/state/{event_id}")
async def get_workflow_state_endpoint(event_id: str) -> Dict:
    """Get current workflow state for an event.

    Returns everything you need to know about the workflow status.
    """
    try:
        state = get_workflow_state(event_id)
        return {
            "status": "success",
            **state
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

