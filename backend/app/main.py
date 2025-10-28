import os

import openai
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .models.booking_model import complete_booking_turn
from .state import conversation_store

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
app = FastAPI()

cors = CORSMiddleware(
    app=app,
    allow_origins=[os.getenv("FRONTEND_URL")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok"}


class Prompt(BaseModel):
    prompt: str


@app.post("/generate-text")
def generate_text(prompt: Prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


class BookingRequest(BaseModel):
    session_id: str
    user_message: str


@app.post("/booking/chat")
def booking_chat(req: BookingRequest):
    """
    Booking chat endpoint

    Request body:
    {
      "session_id": "abc123",
      "user_message": "I can do next Tuesday afternoon"
    }

    Returns:
    { "reply": "...assistant text...", "session_id": "abc123" }

    Notes:
    - History is kept in-memory per session_id (replace with persistent store for production).
    - Model and base URL can be configured via env: BOOKING_MODEL, OPENROUTER_API_KEY, OPENROUTER_BASE_URL.
    """
    # Retrieve existing history for this session_id
    history = conversation_store.get(req.session_id)

    # Call booking agent to get assistant reply
    assistant_msg = complete_booking_turn(history, req.user_message)

    # Update history with user and assistant turns
    conversation_store.append(req.session_id, {"role": "user", "content": req.user_message})
    conversation_store.append(req.session_id, assistant_msg)

    return {"reply": assistant_msg["content"], "session_id": req.session_id}
