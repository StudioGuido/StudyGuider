from telnetlib import SUPDUP
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import asyncpg
import os
from fastapi import status
from fastapi.responses import JSONResponse
from api.auth import verify_jwt

router = APIRouter()
'''allows grouping endpoints'''

@router.get("/api/getTextbooks")
async def getTextbooks_endpoint(user_id = Depends(verify_jwt)):
    supabase_uid = user_id.get("sub")
    if not supabase_uid:
        raise HTTPException(status_code=401, detail="Missing UID")
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD")
        )

        row = await conn.fetchrow("SELECT * FROM user_textbook WHERE user_uid = $1;", supabase_uid)

        if rows == None:
            raise HTTPException(status_code=404, detail="Titles from textbooks not found")

        textbooks = [
            {
                "textbook_id": row["textbook_id"],
            }
        ]

        return textbooks
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        await conn.close()
'''
Fetches all textbooks from the database and returns a list of dictionaries 
containing title, author, description, and image_path.
    
Connects asynchronously to PostgreSQL using environment variables, fetches all rows 
from the 'textbooks' table, and converts them into a JSON-friendly format.
    
Raises HTTPException(404) if no textbooks are found, or HTTPException(500) 
for any database errors.
'''
    





