from fastapi import APIRouter, HTTPException, Depends
import asyncpg
import os
import logging
import uuid
from api.auth import verify_jwt
import logging
router = APIRouter()
logger = logging.getLogger(__name__)
import uuid

@router.get("/api/getTextbooks")
async def getTextbooks_endpoint(user_id = Depends(verify_jwt)):
    request_id = str(uuid.uuid4())
    supabase_uid = user_id.get("sub")
    
    request_id = str(uuid.uuid4())
    if not supabase_uid:
        raise HTTPException(status_code=401, detail="Missing UID")
    conn = None
    try:
        logger.info(f"[{request_id}] Connecting to database")

        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD")
        )

        rows = await conn.fetch(
            "SELECT id, title, status FROM textbooks WHERE user_uid = $1 AND status = 'complete';",
            supabase_uid,
        )

        # if not rows:
        #     raise HTTPException(status_code=404, detail="Titles from textbooks not found")

        return [
            {
                "id": row["id"],
                "title": row["title"],
                "status": row["status"],
            }
            for row in rows
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Database error", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn is not None:
            await conn.close()
'''
Fetches all textbooks from the database and returns a list of dictionaries 
containing title, author, description, and image_path.
    
Connects asynchronously to PostgreSQL using environment variables, fetches all rows 
from the 'textbooks' table, and converts them into a JSON-friendly format.
    
Raises HTTPException(404) if no textbooks are found, or HTTPException(500) 
for any database errors.
'''
    
    
@router.get("/api/getTextbookTitle")
async def get_textbook_title(
    textbook_id: int,
    user_valid=Depends(verify_jwt)
):
    conn = None
    try:
        supabase_uid = user_valid.get("sub")
        if not supabase_uid:
            raise HTTPException(status_code=401, detail="Missing UID")

        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        row = await conn.fetchrow(
            """
            SELECT title
            FROM textbooks
            WHERE id = $1 AND user_uid = $2
            """,
            textbook_id,
            supabase_uid,
        )

        if not row:
            raise HTTPException(status_code=404, detail="Textbook not found")

        return {
            "title": row["title"]
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        if conn:
            await conn.close()





