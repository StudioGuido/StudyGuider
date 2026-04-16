from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
import os
import asyncpg
from fastapi.responses import JSONResponse
from fastapi import status
import logging
import uuid
from api.auth import verify_jwt
import redis.asyncio as redis

logger = logging.getLogger(__name__)
router = APIRouter()

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=int(os.getenv("REDIS_DB", "0")),
)

class ChapterRequest(BaseModel):
    textbook: str
    user_id: str

#Used to reopen a chapter with Redis cache
class ChapterOpenRequest(BaseModel):
    textbook: str
    chapter_title: str
    user_id: str


@router.get("/api/getChapters")
async def getChapters_endpoint(textbook_id: str, user_id = Depends(verify_jwt)):

    '''
    This api is used to retrieve every chapter within a textbook given
    a existing textbook title
    '''

    request_id = str(uuid.uuid4())


    supabase_uid = user_id.get("sub")
    if not supabase_uid:
        raise HTTPException(status_code=401, detail="Missing UID")
    conn = None

    try:
        conn = await asyncpg.connect(
        host=os.getenv("DATABASE_HOST"),
        database=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD")
        )

        logger.debug(f"[{request_id}] Successfully found textbook with id: {textbook_id}")

        rows = await conn.fetch(
            "SELECT chapter_id FROM textbook_chapter WHERE textbook_id = $1;",
            textbook_id
        )

        if not rows:
            logger.warning(f"[{request_id}] No chapters found for textbook_id=%s", textbook_id)
            raise HTTPException(status_code=404, detail="Chapter Titles not found")

        logger.debug(f"[{request_id}] Successfully retrieved all chapters")

        chapters = [row["chapter_id"] for row in rows]

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"response": chapters}
        )
    
    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"[{request_id}] Database error occured")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    finally:
        if conn is not None:
            await conn.close()


@router.get("/api/redis/health")
async def redis_health():
    try:
        pong = await redis_client.ping()
        return {"ok": bool(pong)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")

@router.post("/api/openChapter")
async def openChapter_endpoint(request: ChapterOpenRequest, user_id=Depends(verify_jwt)):
    supabase_uid = user_id.get("sub")
    if not supabase_uid:
        raise HTTPException(status_code=401, detail="Missing UID")

    try:
        redis_key = f"chapter:{request.textbook}:{request.chapter_title}:{supabase_uid}"
        ttl_seconds = 600
        await redis_client.set(redis_key, request.chapter_title, ex=ttl_seconds)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "response": "Chapter opened successfully",
                "active_chapter": request.chapter_title,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")
