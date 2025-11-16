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


@router.delete("/api/deleteUser/{username}")
async def retrieveDeleteUser(username: str):
    """
    API Endpoint for user deletion

    Takes in a username endpoint path paramter and deletes the account associated with that username.
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
    API Endpoint for flash card set creation

    Creates a Flash Card set that references an associated user account and holds
    a title string.

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


# ChatGPT aided in refinement of this method
@router.delete("/api/deleteFlashSet")
async def deleteFlashSet(flashset: FlashcardSet):
    """ "
    API Endpoint for flash card set deletion

    Deletes a flashcard set based on user email and flashcard set name.
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
            SELECT id FROM users WHERE email = $1
            """,
            flashset.user_email,
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Email",
            )

        user_id = user["id"]

        result = await conn.execute(
            """
            DELETE FROM flash_card_set
            WHERE user_id = $1 AND set_title = $2
            """,
            user_id,
            flashset.title,
        )

        if result == "DELETE 0":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Flash set not found",
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Flash set deleted successfully"},
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        if conn:
            await conn.close()


@router.post("/api/addToFlashCardSet")
async def addToFlashCardSet(flashcards: List[Flashcard]):
    """
    API Endpoint for flash card creation

    Adds an List of flash card json objects to an existing flash card set.

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
    API Endpoint for summary creation

    Saves an input summary to an associated user account

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


# VSCode auto coded alot of this (somehow) + Chatgpt helped refine
@router.get("/api/getFlashcardsFromSet")
async def getFlashcardsFromSet(flashset: FlashcardSet):
    """
    API Endpoint for getting all Flashcards in an associated set

    Returns an array of Flash Cards given a user's email and
    the name of the flashcard set.

    NOTE: I am unsure as to how the frontend will display/store the information
    related to the flashcard sets, so currently I am assuming the users will not
    create flashcard sets of a a duplicate name, and therefore we are using the email
    and set name in tandum to return the flash cards. This is open to modification if
    required.
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
            SELECT id FROM users WHERE email = $1
            """,
            flashset.user_email,
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Email",
            )
        user_id = user["id"]

        flashset = await conn.fetchrow(
            """
            SELECT fcset_id, user_id
            FROM flash_card_set
            WHERE user_id = $1 AND set_title = $2
            """,
            user_id,
            flashset.title,
        )

        if not flashset:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Flashcard Set",
            )

        flashset_id = flashset["fcset_id"]
        flashcards = await conn.fetch(
            """
            SELECT fc_id, question, answer
            FROM flash_card
            WHERE fcset_id = $1
            """,
            flashset_id,
        )

        flashcard_list = [dict(row) for row in flashcards]

        return JSONResponse(status_code=200, content={"response": flashcard_list})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        await conn.close()


@router.get("/api/getAllFlashcardSets")
async def getAllFlashcardSets(user_info: User):
    """
    API Endpoint for getting all Flashcard Sets

    Returns an array of Flash Card Sets given the users email
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
            SELECT id FROM users WHERE email = $1
            """,
            user_info.email,
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Email",
            )
        user_id = user["id"]

        flashset = await conn.fetch(
            """
            SELECT fcset_id, set_title
            FROM flash_card_set
            WHERE user_id = $1
            """,
            user_id,
        )
        if not flashset:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No Flashcard Sets",
            )
        flashset_list = [dict(row) for row in flashset]

        return JSONResponse(status_code=200, content={"response": flashset_list})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        await conn.close()
