from fastapi import FastAPI, UploadFile, File, HTTPException
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import openai
from pydantic import BaseModel
import os
from typing import Optional

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
