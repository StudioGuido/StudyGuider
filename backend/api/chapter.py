from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import os
import asyncpg
from fastapi.responses import JSONResponse
from fastapi import status
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class ChapterRequest(BaseModel):
    textbook: str


@router.get("/api/getChapters")
async def getChapters_endpoint(textbook: str):
    '''
    This api is used to retrieve every chapter within a textbook given
    a existing textbook title
    '''
    logger.info("Fetching chapters for textbook=%s", textbook)
    try:
        conn = await asyncpg.connect(
        host=os.getenv("DATABASE_HOST"),
        database=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD")
        )

        textbook_id = await conn.fetchval(
        "SELECT id FROM textbooks WHERE title = $1;",
        textbook)


        if textbook_id is None:
            logger.warning("Textbook not found: %s", textbook)
            raise HTTPException(status_code=404, detail="Textbook not found")

        logger.debug("Successfully found textbook with id: {textbook_id}")

        rows = await conn.fetch(
            "SELECT chapter_title FROM chapters WHERE textbook_id = $1;",
            textbook_id
        )

        if not rows:
            logger.warning("No chapters found for textbook_id=%s", textbook_id)
            raise HTTPException(status_code=404, detail="Chater Titles not found")

        logger.debug("Successfully found retrieved all chapters")

        # select only chapter_titles from row
        chapters = [row["chapter_title"] for row in rows]
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"response": chapters}
        )
    
    except HTTPException:
        raise

    except Exception as e:
        logger.error("Database error occured")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    finally:
        await conn.close()