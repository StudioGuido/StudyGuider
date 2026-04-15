from fastapi import APIRouter, HTTPException, Depends
import asyncpg
import os
from api.auth import verify_jwt

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/api/getTextbooks")
async def getTextbooks_endpoint(user_id = Depends(verify_jwt)):
    supabase_uid = user_id.get("sub")
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
            "SELECT textbook_id, textbook_title, status FROM user_textbook WHERE user_uid = $1;",
            supabase_uid,
        )

        if not rows:
            raise HTTPException(status_code=404, detail="Titles from textbooks not found")

        return [
            {
                "textbook_id": row["textbook_id"],
                "textbook_title": row["textbook_title"],
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
    





