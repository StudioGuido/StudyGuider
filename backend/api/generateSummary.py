from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import os
import asyncpg
from fastapi import status
from fastapi.responses import JSONResponse
import re
import logging
import uuid
import time
from .AIHelper import get_gemini_response
from api.auth import verify_jwt

router = APIRouter()
logger = logging.getLogger(__name__)


# class SummaryRequest(BaseModel):
#     textbook: str
#     chapter: str
    
class SummaryRequest(BaseModel):
    textbook: int
    chapter: int


@router.post("/api/generateSummary")
async def generate_endpoint(request: SummaryRequest, user_valid=Depends(verify_jwt)):
    supabase_uid = user_valid.get("sub")
    
    if not supabase_uid:
        raise HTTPException(status_code=401, detail="Missing UID")

    request_id = str(uuid.uuid4())
    start_time = time.time()

    logger.info(f"[{request_id}] Incoming summary request", extra={
        "textbook": request.textbook,
        "chapter": request.chapter
    })

    # chapter = request.chapter
    # textbook = request.textbook

    conn = None

    try:
        logger.info(f"[{request_id}] Connecting to database")

        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD")
        )

        logger.info(f"[{request_id}] Fetching chapter metadata")

        # res = await conn.fetchrow("""
        #     SELECT c.textbook_id, c.chapter_number
        #     FROM chapters c
        #     JOIN textbooks t ON c.textbook_id = t.id
        #     WHERE t.title = $1 AND c.chapter_title = $2;
        # """, textbook, chapter)

        # if res is None:
        #     logger.warning(f"[{request_id}] Invalid textbook/chapter")
        #     raise HTTPException(status_code=400, detail="Invalid textbook or chapter title")

        # textbook_id = res["textbook_id"]
        # chapter_number = res["chapter_number"]
        
        textbook_id = request.textbook
        chapter_number = request.chapter

        logger.info(f"[{request_id}] Fetching chunks", extra={
            "textbook_id": textbook_id,
            "chapter_number": chapter_number
        })

        all_chunk = await conn.fetch("""
            SELECT chunk_text 
            FROM chapter_embeddings 
            WHERE textbook_id = $1 AND chapter_number = $2;
        """, textbook_id, chapter_number)

        if not all_chunk:
            logger.warning(f"[{request_id}] No chunks found")
            raise HTTPException(status_code=404, detail="No chunks found in database")

        logger.info(f"[{request_id}] Retrieved chunks", extra={
            "chunk_count": len(all_chunk)
        })

        # Helper function to clean a single chunk
        def clean_chunk(text):
            text = text.strip()
            text = re.sub(r"\n+", " ", text)
            return text

        # Combine chunks
        chapter_text = " ".join(
            clean_chunk(row["chunk_text"])
            for row in all_chunk
            if row["chunk_text"] and row["chunk_text"].strip()
        )

        logger.info(f"[{request_id}] Built chapter text", extra={
            "char_length": len(chapter_text)
        })

        # Build prompt
        prompt = f"""
        Summarize the following chapter so that a student can easily understand the main ideas, key concepts, and important details. Use clear and simple language.

        Chapter Content:
        {chapter_text}
        """

        logger.info(f"[{request_id}] Calling Gemini")

        try:
            modelResponse = await get_gemini_response(prompt)
        except Exception as e:
            logger.error(f"[{request_id}] Gemini API failed", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")

        logger.info(f"[{request_id}] Summary generated", extra={
            "response_length": len(modelResponse) if modelResponse else 0,
            "duration_sec": round(time.time() - start_time, 2)
        })

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"response": modelResponse}
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        if conn:
            await conn.close()
            logger.info(f"[{request_id}] DB connection closed")