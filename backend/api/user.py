from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import asyncpg
import logging
from api.auth import verify_jwt

router = APIRouter()
logger = logging.getLogger(__name__)

# --- 1. CREATE USER (Sync with Supabase) ---
@router.post("/api/createUser")
async def create_user(user_valid=Depends(verify_jwt)):
    supabase_uid = user_valid.get("sub")
    
    if not supabase_uid:
        raise HTTPException(status_code=401, detail="Missing UID")

    conn = None
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        row = await conn.fetchrow(
            """
            INSERT INTO users (supabase_uid)
            VALUES ($1)
            ON CONFLICT (supabase_uid) DO NOTHING
            RETURNING supabase_uid;
            """,
            supabase_uid,
        )

        user_dict = dict(row)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"response": {
                "supabase_uid": str(user_dict["supabase_uid"]),
            }},
        )
    except Exception as e:
        logger.error(f"Error in createUser: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn: await conn.close()


# --- 2. DELETE USER ---
@router.delete("/api/users/me")
async def delete_user(user_valid=Depends(verify_jwt)):
    supabase_uid = user_valid.get("sub")
    conn = None
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        deleted = await conn.fetchrow(
            "DELETE FROM users WHERE supabase_uid=$1 RETURNING supabase_uid",
            supabase_uid,
        )
        if not deleted:
            raise HTTPException(status_code=404, detail="User not found")

        return {"deleted_user": str(deleted["supabase_uid"])}
    except Exception as e:
        logger.error(f"Error in delete_user: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        if conn: await conn.close()
