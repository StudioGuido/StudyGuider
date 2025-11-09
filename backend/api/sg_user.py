from fastapi import APIRouter, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, EmailStr, Field
import os
import asyncpg
from fastapi.responses import JSONResponse
from fastapi import status
from typing import List

router = APIRouter()


class User(BaseModel):
    username: str
    email: str


class FlashcardSet(BaseModel):
    user_email: str
    title: str

class Flashcard(BaseModel):
    flashcardset: FlashcardSet
    question: str
    answer: str

class Summary(BaseModel):
    user_email: str
    title: str
    content: str


@router.post("/api/createUser")
async def createUser(userData: User):
    """
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


@router.delete("/api/deleteUser/{username}")
async def retrieveDeleteUser(username: str):
    # username = userData.username
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
        WHERE username = $1
        """,
            username,
        )

        print(user)

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


@router.post("/api/createFlashCardSet")
async def createFlashCardSet(flashset: FlashcardSet):
    """
    example json input:

    json = {
    "user_email": "pwex@gmail.com",
    "title": "Basic Math FlashCards",
    }

    """
    user_email = flashset.user_email
    title = flashset.title
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )
        try:
            user = await conn.fetchrow(
                """
            SELECT id
            FROM users
            WHERE email = $1
            """,
                user_email,
            )
        except Exception as e:
            raise HTTPException(500, f"Error in finding valid user: {e}")
        user_dict = dict(user)
        user_id = user_dict["id"]
        try:
            row = await conn.fetchrow(
                """
            INSERT INTO flash_card_set
              (set_title, user_id)
            VALUES
              ($1, $2)
            RETURNING
              fcset_id, set_title, user_id;
            """,
                title,
                user_id,
            )

        except Exception as e:
            raise HTTPException(500, f"Error in making a flashcard set: {e}")

        user_dict = dict(row)
        response_content = {
            "fcset_id": user_dict["fcset_id"],
            "set_title": user_dict["set_title"],
            "user_id": user_dict["user_id"],
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

@router.delete("/api/deleteFlashSet/{set_name}")
async def deleteFlashSet(set_name: str):
    # username = userData.username
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )
        flash_set = await conn.fetchrow(
            """
        SELECT id
        FROM flash_card_set
        WHERE title = $1
        """,
            set_name,
        )


        if not flash_set:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Flashcard Set name"
            )

        # remove the user
        flash_set_dict = dict(flash_set)
        flash_set = await conn.execute(
            """
        DELETE FROM flash_card_set
        WHERE id = $1
        """,
            flash_set_dict["id"],
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"response": flash_set}
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        await conn.close()

@router.post("/api/addToFlashCardSet")
async def addToFlashCardSet(flashcards: List[Flashcard]):
    """
    example json input:

    json = [
        {
        "set_title": "Basic Math FlashCards", 
        "question": "1 + 1", 
        "answer": "2",  
        },
        {
        "set_title": "Basic Math FlashCards", 
        "question": "1 - 1", 
        "answer": "0",  
        },
        {
        "set_title": "Basic Math FlashCards", 
        "question": "1 * 1", 
        "answer": "1",  
        },
        {
        "set_title": "Basic Math FlashCards", 
        "question": "1 / 1", 
        "answer": "1",  
        },
        {
        "set_title": "Basic Math FlashCards", 
        "question": "1 ^ 1", 
        "answer": "1",  
        },
    ]

    """
    set_title = flashcards[0].flashcardset.title
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )
        try:
            fcset = await conn.fetchrow(
                """
            SELECT fcset_id
            FROM flash_card_set
            WHERE set_title = $1
            """,
                set_title,
            )
        except Exception as e:
            raise HTTPException(500, f"Error in finding flashcard set: {e}")
        fcset_dict = dict(fcset)
        fcset_id = fcset_dict["fcset_id"]
        response_content = {}
        try:
            for flashcard in flashcards:
                row = await conn.fetchrow(
                    """
                INSERT INTO flash_card
                (fcset_id, question, answer)
                VALUES
                ($1, $2, $3)
                RETURNING
                fc_id, question, answer;
                """,
                    fcset_id,
                    flashcard.question,
                    flashcard.answer,
                )
                response_content.update(dict(row))

        except Exception as e:
            raise HTTPException(500, f"Error in making flashcard: {e}")

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

@router.post("/api/saveSummary")
async def saveSummary(summ: Summary):
    """
    example json input:

    json = {
    "user_email": "pwex@gmail.com",
    "title": "My Summary",
    "content": "This is an excerpt from ChatGPT"
    }

    """
    user_email = summ.user_email
    title = summ.title
    content = summ.content
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )
        try:
            user = await conn.fetchrow(
                """
            SELECT id
            FROM users
            WHERE email = $1
            """,
                user_email,
            )
        except Exception as e:
            raise HTTPException(500, f"Error in finding valid user: {e}")
        user_dict = dict(user)
        user_id = user_dict["id"]
        try:
            row = await conn.fetchrow(
                """
            INSERT INTO summary
              (user_id, title, content)
            VALUES
              ($1, $2, $3)
            RETURNING
              summary_id, title, content;
            """,
                user_id,
                title,
                content,
            )

        except Exception as e:
            raise HTTPException(500, f"Error in saving a summary: {e}")

        summ_dict = dict(row)
        response_content = {
            "summary_id": summ_dict["summary_id"],
            "title": summ_dict["title"],
            "content": summ_dict["content"],
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
