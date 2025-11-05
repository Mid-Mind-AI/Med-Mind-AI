"""Router for pre-visit questions flow."""
from typing import Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.booking_agent_workflow import (
    generate_pre_visit_report,
    get_next_pre_visit_question,
    submit_pre_visit_answer,
)
from app.models.pre_visit_questions import get_qa_history
from app.models.pre_visit_report import get_report

router = APIRouter(prefix="/pre-visit", tags=["Pre-Visit"])


class QuestionRequest(BaseModel):
    """Request to get the next question."""
    event_id: str = Field(..., description="Event ID")


class AnswerRequest(BaseModel):
    """Request to submit an answer."""
    event_id: str = Field(..., description="Event ID")
    question: str = Field(..., description="The question that was asked")
    answer: str = Field(..., description="The patient's answer")


class GenerateReportRequest(BaseModel):
    """Request to generate the final report."""
    event_id: str = Field(..., description="Event ID")


@router.get("/question/{event_id}")
async def get_next_question(event_id: str) -> Dict:
    """Get the next pre-visit question for an event.

    Returns:
        - question: The next question to ask
        - question_count: Number of questions asked so far
        - is_complete: Whether 7 questions have been asked
    """
    try:
        result = get_next_pre_visit_question(event_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/answer")
async def submit_answer(payload: AnswerRequest) -> Dict:
    """Submit an answer to a pre-visit question.

    Returns:
        - status: Success status
        - question_count: Updated question count
        - is_complete: Whether 7 questions have been asked
        - next_question: The next question (if any)
    """
    try:
        result = submit_pre_visit_answer(
            event_id=payload.event_id,
            question=payload.question,
            answer=payload.answer,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-report")
async def generate_report_endpoint(payload: GenerateReportRequest) -> Dict:
    """Generate the pre-visit report from Q&A history.

    This should be called after 7 questions have been answered.
    """
    try:
        result = generate_pre_visit_report(payload.event_id)

        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Failed to generate report"))

        return {
            "status": "success",
            "report": result["report"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{event_id}")
async def get_question_history(event_id: str) -> Dict:
    """Get the full Q&A history for an event."""
    try:
        qa_history = get_qa_history(event_id)
        saved_report = get_report(event_id)

        return {
            "qa_history": qa_history,
            "report": saved_report,
            "question_count": len(qa_history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

