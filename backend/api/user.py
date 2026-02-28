from fastapi import APIRouter, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import os
import asyncpg
from fastapi.responses import JSONResponse
from fastapi import status
from typing import List

router = APIRouter()


class User(BaseModel):
    username: str
    email: str


@router.post("/api/createUser")
async def SGUser(userData: User):
    """
    API Endpoint for user creation

    Current Implementation only holds a username and email value, with OAuth
    functionality TBI.

    example json input:

    json = {
    "username": "pwex",
    "email": "pwex@gmail.com",
    }
    """
    username = userData.username
    email = userData.email

    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )
        try:
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

        except Exception as e:
            raise HTTPException(500, f"Error in making a user: {e}")

        user_dict = dict(row)
        # token = create_access_token(subject=user_dict["username"])

        response_content = {
            "id": user_dict["id"],
            "username": user_dict["username"],
            "email": user_dict["email"],
        }
        print(response_content)
        try:
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content=jsonable_encoder({"response": response_content}),
            )
        except Exception as e:
            print("Serialization error:", e)
            raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        await conn.close()


@router.delete("/api/deleteUser/{email}")
async def SGUser(email: str):
    """
    API Endpoint for user deletion

    Takes in a email endpoint path paramter and deletes the account associated with that email.
    """
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )
        user = await conn.fetchrow(
            """
        SELECT id
        FROM users
        WHERE email = $1
        """,
            email,
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username"
            )

        # remove the user
        user_dict = dict(user)
        user = await conn.execute(
            """
        DELETE FROM users
        WHERE id = $1
        """,
            user_dict["id"],
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"response": user_dict}
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        await conn.close()


@router.put("/api/updateUser")
async def SGUser(userData: User):
    """
    API Endpoint for user updates

    Takes in a User basemodel with and email and an username to update to.
    """
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        user = await conn.execute(
            """
            UPDATE users
            SET username = $1
            WHERE email = $2
            """,
            userData.username,
            userData.email,
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Email"
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"response": "username Update Sucessful"},
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        await conn.close()


@router.get("/api/getUsername/{email}")
async def SGUser(email: str):
    """
    API Endpoint for getting the username of a user account given the email.
    """
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
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
            )

        user_dict = dict(user)
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"response": user_dict}
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        await conn.close()