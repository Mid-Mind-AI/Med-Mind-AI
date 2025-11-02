from fastapi import FastAPI, UploadFile, File, HTTPException
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import openai
from pydantic import BaseModel
import os
from typing import Optional
from app.routers import calendar as calendar_router
from app.routers import report
from app.routers import booking as booking_router
from app.routers import transcribe as transcribe_router

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# CORS for local Next.js dev servers
app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:3000", "http://localhost:3001"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Mount feature routers
app.include_router(calendar_router.router)
app.include_router(report.router)
app.include_router(booking_router.router)
app.include_router(transcribe_router.router)


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
