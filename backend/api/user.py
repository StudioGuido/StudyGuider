from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import os
import asyncpg
from fastapi.responses import JSONResponse
from fastapi import status
from typing import List
from api.auth import verify_jwt

router = APIRouter()


class User(BaseModel):
    username: str


@router.post("/api/createUser")
async def create_user(user_valid=Depends(verify_jwt)):

    username = _username_from_payload(user_valid)
    supabase_uid = user_valid.get("sub")
    if not supabase_uid:
        raise HTTPException(status_code=401, detail="Missing supabase uid in token")

    conn = None

    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        # Upsert by Supabase UID so the identity is stable even if email changes.
        row = await conn.fetchrow(
            """
            INSERT INTO users (supabase_uid, username)
            VALUES ($1, $2)
            ON CONFLICT (supabase_uid) DO UPDATE
            SET username = EXCLUDED.username
            RETURNING supabase_uid, username;
            """,
            supabase_uid,
            username,
        )

        user_dict = dict(row)

        response_content = {
            "supabase_uid": user_dict["supabase_uid"],
            "username": user_dict["username"],
        }

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder({"response": response_content}),
        )

    except Exception:
        raise HTTPException(status_code=500, detail="Database error")

    finally:
        if conn:
            await conn.close()


@router.delete("/api/users/me")
async def delete_user(user_valid=Depends(verify_jwt)):

    supabase_uid = user_valid.get("sub")
    if not supabase_uid:
        raise HTTPException(status_code=401, detail="Missing supabase uid in token")
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

        return {"deleted_user": supabase_uid}

    finally:
        if conn:
            await conn.close()


@router.put("/api/updateUser")
async def update_user(userData: User, user_valid=Depends(verify_jwt)):

    supabase_uid = user_valid.get("sub")
    if not supabase_uid:
        raise HTTPException(status_code=401, detail="Missing supabase uid in token")

    conn = None
    
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        result = await conn.execute(
            """
            UPDATE users
            SET username = $1
            WHERE supabase_uid = $2
            """,
            userData.username,
            supabase_uid,
        )

        if result == "UPDATE 0":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"response": "username Update Successful"},
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=500, detail="Database error")

    finally:
        if conn:
            await conn.close()


def _username_from_payload(payload: dict) -> str:
    """Derive username from JWT payload: user_metadata.username or a safe default."""
    meta = payload.get("user_metadata") or {}
    if isinstance(meta, dict) and meta.get("username"):
        return str(meta["username"])[:150]
    return "user"[:150]


@router.get("/api/users/me")
async def get_username(user_valid=Depends(verify_jwt)):
    
    supabase_uid = user_valid.get("sub")
    if not supabase_uid:
        raise HTTPException(status_code=401, detail="Missing supabase uid in token")
    conn = None
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        user = await conn.fetchrow(
            """
            SELECT supabase_uid, username
            FROM users
            WHERE supabase_uid = $1
            """,
            supabase_uid,
        )

        if not user:
            username = _username_from_payload(user_valid)
            user = await conn.fetchrow(
                """
                INSERT INTO users (supabase_uid, username)
                VALUES ($1, $2)
                RETURNING supabase_uid, username
                """,
                supabase_uid,
                username,
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"response": dict(user)},
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=500, detail="Database error")

    finally:
        if conn:
            await conn.close()