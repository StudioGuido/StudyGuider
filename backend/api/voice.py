import os
import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
import logging
import uuid

load_dotenv(".env")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/api/session")
async def create_session():
    """
    This api is used to send token to frontend to connect 
    to the realtime api client, using specific version and instructions
    """
    request_id = str(uuid.uuid4())

    logger.info(f"[{request_id}] Connecting to realtime API...")
    try:
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
    
    except httpx.HTTPStatusError as e:
        logger.error(f"[{request_id}] OpenAI returned error: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail="OpenAI API error")

    except httpx.RequestError as e:
        logger.error(f"[{request_id}] Network error: {e}")
        raise HTTPException(status_code=503, detail="Could not reach OpenAI")

    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")