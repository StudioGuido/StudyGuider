import os
import httpx
from dotenv import load_dotenv
from fastapi import APIRouter

load_dotenv(".env")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

router = APIRouter()

@router.get("/session")
async def create_session():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/realtime/sessions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-realtime-preview",
                "voice": "alloy",
                "instructions": "You are a tutor and you are meant to provide helpful explanations in english",
                "input_audio_transcription": {
                    "model": "whisper-1"
                }
            }
        )
        return response.json()