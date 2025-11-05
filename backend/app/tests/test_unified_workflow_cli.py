#!/usr/bin/env python3
"""
CLI for testing the unified workflow endpoint.

This CLI uses the /workflow/process endpoint which handles:
- Booking appointments
- Pre-visit questions
- Report generation

Make sure to run the FastAPI server first: uvicorn app.main:app --reload
"""

import json
from typing import Any, Dict, List

import requests

# API base URL
API_BASE = "http://localhost:8000"
WORKFLOW_ENDPOINT = f"{API_BASE}/workflow/process"
STATE_ENDPOINT = f"{API_BASE}/workflow/state"

# ANSI styling for clearer CLI output
RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"


def call_workflow(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Call the unified workflow endpoint."""
    try:
        response = requests.post(WORKFLOW_ENDPOINT, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        # Print HTTP errors (like 400, 500) with details
        try:
            error_detail = e.response.json()
            print(f"ERROR: HTTP {e.response.status_code} - {error_detail.get('detail', str(e))}")
        except (ValueError, AttributeError):
            print(f"ERROR: HTTP {e.response.status_code if hasattr(e, 'response') else 'Unknown'} - {str(e)}")
        return {}
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Request failed - {str(e)}")
        return {}


def get_workflow_state(event_id: str) -> Dict[str, Any]:
    """Get workflow state for an event."""
    try:
        response = requests.get(f"{STATE_ENDPOINT}/{event_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return {}


def print_response(response: Dict[str, Any]) -> None:
    """Print only model output."""
    if "message" in response:
        print(f"{GREEN}Assistant:{RESET} {response['message']}")

    if "next_question" in response:
        print(f"{CYAN}Question:{RESET} {response['next_question']}")

    if "report" in response:
        print(json.dumps(response["report"], indent=2))


def booking_flow():
    """Handle the booking flow with conversation history."""
    chat_history: List[Dict[str, str]] = []
    event_id = None

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            return None

        if user_input.lower() == "skip":
            return None

        if not user_input:
            continue

        # visual spacing after the user's input
        print()

        # Add user message to history
        chat_history.append({"role": "user", "content": user_input})

        # Call workflow with booking message
        payload = {
            "user_message": user_input,
            "chat_history": chat_history[:-1]  # Send history without current message
        }

        response = call_workflow(payload)

        if not response:
            continue

        # Add assistant response to history
        if "message" in response:
            chat_history.append({"role": "assistant", "content": response["message"]})

        # Check if booking is complete BEFORE printing
        if response.get("status") == "booking_complete":
            event_id = response.get("event_id")
            initial_question = response.get("next_question")
            # Print only the booking message, not the question (question will be handled in questions_flow)
            if "message" in response:
                print(response['message'])
            return (event_id, initial_question)

        # For booking_in_progress, print the message normally
        print_response(response)

        # Check if still in progress
        if response.get("status") == "booking_in_progress":
            continue

    return None


def questions_flow(event_id: str, initial_question: str = None):
    """Handle the pre-visit questions flow."""
    current_question = initial_question
    question_count = 0

    # If we already have the first question from booking, print it and use it
    # Otherwise, fetch it
    if current_question:
        # Print the question we got from booking completion
        print()  # spacing after the user's last input
        print(f"{CYAN}Question:{RESET} {current_question}")
        question_count = 0
    else:
        # Fetch the first question
        payload = {"event_id": event_id}
        response = call_workflow(payload)

        if not response:
            return False

        # spacing after the user's answer
        print()
        print_response(response)
        current_question = response.get("next_question")
        question_count = response.get("question_count", 0)

    if not current_question:
        return True

    # Answer questions
    while question_count < 7:
        # Check if we need to get the next question
        if not current_question:
            # Get next question
            payload = {"event_id": event_id}
            response = call_workflow(payload)
            if response:
                current_question = response.get("next_question")
                question_count = response.get("question_count", 0)
                is_complete = response.get("is_questions_complete", False)

                # Check if questions are already complete
                if is_complete or question_count >= 7:
                    return True

                if current_question:
                    print_response(response)
                else:
                    # No more questions
                    return True
            else:
                break

        # Get user input for the current question
        user_answer = input("You: ").strip()

        if user_answer.lower() in ["exit", "quit"]:
            return False

        if user_answer.lower() == "skip":
            return False

        if not user_answer:
            continue

        # Submit answer
        payload = {
            "event_id": event_id,
            "question": current_question,
            "answer": user_answer
        }

        response = call_workflow(payload)

        if not response:
            continue

        print()  # blank line between prompts
        print_response(response)

        # Check if complete - exit immediately if questions are done
        if response.get("status") == "questions_complete":
            return True

        # Also check the is_questions_complete flag
        if response.get("is_questions_complete", False):
            return True

        # Get next question
        current_question = response.get("next_question")
        question_count = response.get("question_count", 0)

        # Double-check: if we've answered 7 questions, exit
        if question_count >= 7:
            return True

    return True


def report_flow(event_id: str):
    """Automatically generate and display the report."""
    print("\nGenerating your pre-visit report...")

    payload = {
        "event_id": event_id,
        "generate_report": True
    }

    response = call_workflow(payload)

    if not response:
        print("ERROR: Failed to generate report - no response from server")
        return

    # Check for error status
    if response.get("status") == "error":
        print(f"ERROR: {response.get('message', 'Report generation failed')}")
        return

    # Check if report was generated successfully
    if response.get("status") == "report_generated":
        print_response(response)
        print("\n" + "="*60)
        print("Thank you for completing the pre-visit questionnaire!")
        print("Your report has been generated and saved.")
        print("Have a great day!")
        print("="*60)
    else:
        # Unexpected status
        print(f"ERROR: Unexpected status '{response.get('status')}'")
        print(f"Response: {json.dumps(response, indent=2)}")


def main():
    """Main CLI loop."""
    try:
        # Greeting message at start of CLI execution
        print("Hi, How can I help you?")
        # Step 1: Booking
        booking_result = booking_flow()

        if not booking_result:
            return

        # booking_flow returns (event_id, initial_question) or None
        if isinstance(booking_result, tuple):
            event_id, initial_question = booking_result
        else:
            event_id = booking_result
            initial_question = None

        # Step 2: Questions
        questions_complete = questions_flow(event_id, initial_question)

        if not questions_complete:
            return

        # Step 3: Report
        report_flow(event_id)

    except KeyboardInterrupt:
        pass
    except Exception:
        pass


if __name__ == "__main__":
    main()

