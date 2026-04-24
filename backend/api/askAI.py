from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Literal
from uuid import UUID
import logging
import uuid
import time

from google.genai import errors as genai_errors

from .AIHelper import get_gemini_response
from .embedding_utils import generate_contextHelper
from api.auth import verify_jwt


router = APIRouter()
logger = logging.getLogger(__name__)


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    text: str


class AskAIRequest(BaseModel):
    textbook_id: UUID
    chapter_number: int
    messages: List[ChatMessage]


def format_history(messages: List[ChatMessage]) -> str:
    lines = []
    for m in messages:
        speaker = "User" if m.role == "user" else "Assistant"
        lines.append(f"{speaker}: {m.text.strip()}")
    return "\n".join(lines)


@router.post("/api/askAI")
async def ask_ai(request: AskAIRequest, user_valid=Depends(verify_jwt)):
    if not user_valid.get("sub"):
        raise HTTPException(status_code=401, detail="Missing UID")

    if not request.messages:
        raise HTTPException(status_code=400, detail="messages cannot be empty")

    latest = request.messages[-1]
    if latest.role != "user":
        raise HTTPException(
            status_code=400,
            detail="Latest message must be from the user",
        )

    request_id = str(uuid.uuid4())
    start_time = time.time()

    logger.info(
        f"[{request_id}] askAI request",
        extra={
            "textbook": str(request.textbook_id),
            "chapter": request.chapter_number,
            "turns": len(request.messages),
        },
    )

    try:
        # Retrieval uses only the latest user message. Short follow-ups
        # ("explain more") will embed poorly — acceptable for now.
        context_str = await generate_contextHelper(
            latest.text,
            str(request.chapter_number),
            request.textbook_id,
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception(f"[{request_id}] Context retrieval failed")
        raise HTTPException(status_code=500, detail="Context retrieval failed")

    history_str = format_history(request.messages[:-1])

    prompt = f"""You are a study assistant helping a student understand a textbook chapter. Use the retrieved context below when it is relevant. Use the prior conversation to resolve references like "that", "it", or "explain more". Keep answers concise and clear.

Retrieved context from the chapter:
{context_str}

Prior conversation:
{history_str if history_str else "(no prior messages)"}

Latest user question:
{latest.text}

Answer the latest user question. If the retrieved context does not apply, rely on the conversation and general knowledge, or say you are not sure."""

    try:
        answer = await get_gemini_response(prompt)
    except genai_errors.APIError as e:
        gemini_status = getattr(e, "code", None) or 0
        logger.warning(
            f"[{request_id}] Gemini API error: status={gemini_status} message={getattr(e, 'message', str(e))}"
        )
        if gemini_status == 503:
            raise HTTPException(
                status_code=503,
                detail="The AI service is currently overloaded. Please try again in a moment.",
            )
        if gemini_status == 429:
            raise HTTPException(
                status_code=429,
                detail="Rate limit reached. Please try again shortly.",
            )
        raise HTTPException(status_code=502, detail="Model generation failed")
    except Exception:
        logger.exception(f"[{request_id}] Gemini call failed")
        raise HTTPException(status_code=502, detail="Model generation failed")

    logger.info(
        f"[{request_id}] askAI success",
        extra={
            "duration_sec": round(time.time() - start_time, 2),
            "response_length": len(answer) if answer else 0,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"response": answer},
    )
