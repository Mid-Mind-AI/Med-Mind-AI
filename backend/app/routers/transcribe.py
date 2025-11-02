from fastapi import APIRouter, UploadFile, File, HTTPException
from faster_whisper import WhisperModel
import os
import tempfile
import asyncio
from concurrent.futures import ThreadPoolExecutor

router = APIRouter(prefix="/transcribe", tags=["transcribe"])

# Initialize Whisper model (load once on server start)
# Using base model - use "tiny", "base", "small", "medium", "large" for better accuracy
model = WhisperModel("base", device="cpu", compute_type="int8")

# Thread pool for running inference in background
executor = ThreadPoolExecutor(max_workers=2)

@router.post("/audio")
async def transcribe_audio(audio: UploadFile = File(...)):
    """
    Transcribe audio file using Faster-Whisper (local, free)
    Accepts audio files in various formats (mp3, mp4, mpeg, mpga, m4a, wav, webm)
    """
    try:
        # Read file contents
        contents = await audio.read()

        # Check file size (reasonable limit for local processing)
        if len(contents) > 100 * 1024 * 1024:  # 100MB
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 100MB")

        # Create temporary file to save audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_file:
            tmp_file.write(contents)
            tmp_file_path = tmp_file.name

        try:
            # Run transcription in thread pool (faster-whisper is synchronous)
            loop = asyncio.get_event_loop()
            segments, info = await loop.run_in_executor(
                executor,
                lambda: model.transcribe(tmp_file_path)
            )

            # Extract text from segments
            transcript_text = " ".join([segment.text for segment in segments])

            return {"text": transcript_text}
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
