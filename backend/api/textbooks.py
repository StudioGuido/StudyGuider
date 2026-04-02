from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import asyncpg
import os
from fastapi import status
from fastapi.responses import JSONResponse
import logging
import uuid

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/api/getTextbooks")
async def getTextbooks_endpoint():

    request_id = str(uuid.uuid4())
    logger.info(f"[{request_id}] GET /api/getTextbooks called")

    try:
        logger.info(f"[{request_id}] Connecting to database")

        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD")
        )
        
        logger.info(f"[{request_id}] Fetching textbook from database")
        rows = await conn.fetch("SELECT * FROM textbooks;")

        if rows == None:
            logger.warning(f"[{request_id}] No textbooks found")
            raise HTTPException(status_code=404, detail="Titles from textbooks not found")

        textbooks = [
            {
                "title": row["title"],
                "author": row["author"],
                "description": row["description"],
                "image_path": row["image_path"]
            }
            for row in rows
        ]

        logger.info(f"[{request_id}] Successfully fetched {len(textbooks)} textbook(s)")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"response": textbooks}
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Database error", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        await conn.close()
        logger.info(f"[{request_id}] DB connection closed")
'''
Fetches all textbooks from the database and returns a list of dictionaries 
containing title, author, description, and image_path.
    
Connects asynchronously to PostgreSQL using environment variables, fetches all rows 
from the 'textbooks' table, and converts them into a JSON-friendly format.
    
Raises HTTPException(404) if no textbooks are found, or HTTPException(500) 
for any database errors.
'''
    





