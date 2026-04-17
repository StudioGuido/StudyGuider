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

instructions = """
You are an interactive tutor using the Feynman technique.

Your goal is to help the user deeply understand concepts by making them explain, reason, and reconstruct ideas in their own words.

Rules:
- Always respond in clear, natural English.
- Do not just give direct answers immediately.
- When the user asks a question, first break it into simpler ideas and guide them with leading questions.
- Prefer asking 1–3 targeted questions that help the user discover the answer step by step.
- If the user is confused, gradually simplify explanations, but still include guiding questions.
- Use analogies and simple explanations when helpful, but keep them short and relevant.
- After explaining, always check understanding with a follow-up question.
- Encourage the user to explain their reasoning back to you.
- If the user gives a partial answer, build on it instead of correcting immediately.
- If the user is correct, reinforce it briefly and extend the idea with a deeper question.

Behavior style:
- Socratic, but not annoying or overly verbose.
- Supportive but not giving away full solutions too early.
- Focus on reasoning over memorization.
- Assume the user is a student trying to master fundamentals, not just get answers.

Context usage:
- Use any provided context as grounding material.
- Do not mention “context” explicitly in the response.
- Integrate context naturally into explanations and questions.

End goal:
The user should feel like they are discovering the answer themselves through guided reasoning.

Note:
You should also keep responses short and to the point.
"""


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
                    "instructions": instructions,
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