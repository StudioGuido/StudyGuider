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
async def create_user(userData: User):

    username = userData.username
    email = userData.email

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
            INSERT INTO users
              (username, email)
            VALUES
              ($1, $2)
            RETURNING
              id, username, email;
            """,
            username,
            email,
        )

        user_dict = dict(row)

        response_content = {
            "id": user_dict["id"],
            "username": user_dict["username"],
            "email": user_dict["email"],
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

    email = user_valid["email"]
    conn = None

    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        db_user = await conn.fetchrow(
            """
            SELECT id FROM users WHERE email=$1
            """,
            email,
        )

        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        await conn.execute(
            "DELETE FROM users WHERE id=$1",
            db_user["id"],
        )

        return {"deleted_user": email}

    finally:
        if conn:
            await conn.close()


@router.put("/api/updateUser")
async def update_user(userData: User, user_valid=Depends(verify_jwt)):

    email = user_valid["email"]

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
            WHERE email = $2
            """,
            userData.username,
            email,
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


@router.get("/api/users/me")
async def get_username(user_valid=Depends(verify_jwt)):

    email = user_valid["email"]
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
            SELECT id, username
            FROM users
            WHERE email = $1
            """,
            email,
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
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