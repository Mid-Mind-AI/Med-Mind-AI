"""Unified workflow orchestrator for booking and pre-visit agents.

This module provides internal Python functions for orchestrating agents:
- Booking agent (conversational booking)
- Pre-visit questions agent
- Pre-visit report generation

These functions are used by the routers (endpoints) to provide a cleaner interface.
All agents work together seamlessly through this workflow.
"""

from app.agents.booking_agent_workflow import (
    generate_pre_visit_report,
    get_next_pre_visit_question,
    get_workflow_state,
    process_booking_message,
    submit_pre_visit_answer,
)

__all__ = [
    "process_booking_message",
    "get_next_pre_visit_question",
    "submit_pre_visit_answer",
    "generate_pre_visit_report",
    "get_workflow_state",
]

