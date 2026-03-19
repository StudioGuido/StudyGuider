from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import os
import asyncpg
from fastapi.responses import JSONResponse
from typing import List
from api.auth import verify_jwt

router = APIRouter(
    prefix="/api",
    tags=["user_studymat"],
)


class User(BaseModel):
    username: str | None = None


class FlashcardSet(BaseModel):
    # Backward-compatible: we no longer use this server-side, identity comes from JWT `sub`.
    user_email: str | None = None
    title: str


class Flashcard(BaseModel):
    flashcardset: FlashcardSet
    question: str
    answer: str


class Summary(BaseModel):
    # Backward-compatible: we no longer use this server-side, identity comes from JWT `sub`.
    user_email: str | None = None
    title: str
    content: str


def _username_from_payload(payload: dict) -> str:
    """Derive username from JWT payload: user_metadata.username or a safe default."""
    meta = payload.get("user_metadata") or {}
    if isinstance(meta, dict) and meta.get("username"):
        return str(meta["username"])[:150]
    return "user"


async def _get_or_create_user_id(conn: asyncpg.Connection, user_valid: dict) -> str:
    """
    Resolve app `users.supabase_uid` (primary key) from Supabase JWT `sub`.
    Creates the user row if it doesn't exist.
    """
    user_uid = user_valid.get("sub")
    if not user_uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing supabase uid in token")

    user = await conn.fetchrow(
        "SELECT supabase_uid FROM users WHERE supabase_uid = $1",
        user_uid,
    )
    if user:
        return str(user["supabase_uid"])

    username = _username_from_payload(user_valid)
    created = await conn.fetchrow(
        """
        INSERT INTO users (supabase_uid, username)
        VALUES ($1, $2)
        ON CONFLICT (supabase_uid) DO UPDATE
        SET username = EXCLUDED.username
        RETURNING supabase_uid
        """,
        user_uid,
        username,
    )
    return str(created["supabase_uid"])


@router.post("/api/createFlashCardSet")
async def flashCardSet(flashset: FlashcardSet, user_valid=Depends(verify_jwt)):
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
    user_uid = user_valid.get("sub")
    if not user_uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing supabase uid in token")
    title = flashset.title
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )
        user_id = await _get_or_create_user_id(conn, user_valid)
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


@router.delete("/api/deleteFlashSet")
async def flashCardSet(flashset: FlashcardSet, user_valid=Depends(verify_jwt)):
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

        user_id = await _get_or_create_user_id(conn, user_valid)

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


@router.put("/api/updateFlashSet/{update_title}")
async def flashCardSet(update_title: str, flashset: FlashcardSet, user_valid=Depends(verify_jwt)):
    """ "
    API Endpoint for updating name of flashcard set.
    """
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )
        user_id = await _get_or_create_user_id(conn, user_valid)

        fcs = await conn.execute(
            """
            UPDATE flash_card_set
            SET set_title = $1
            WHERE user_id = $2 AND set_title = $3
            """,
            update_title,
            user_id,
            flashset.title,
        )
        if not fcs:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Flashcard Set does not exist",
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"response": "Flashcard Set Title Update Sucessful"},
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        if conn:
            await conn.close()


@router.post("/api/addToFlashCardSet")
async def addToFlashCardSet(flashcards: List[Flashcard], user_valid=Depends(verify_jwt)):
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
    user_uid = user_valid.get("sub")
    if not user_uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing supabase uid in token")

    set_title = flashcards[0].flashcardset.title
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )
        user_id = await _get_or_create_user_id(conn, user_valid)

        fcset = await conn.fetchrow(
            """
            SELECT fcset_id
            FROM flash_card_set
            WHERE user_id = $1 AND set_title = $2
            """,
            user_id,
            set_title,
        )
        if not fcset:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Flash Card Set: {set_title} Does not Exist",
            )
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
async def summary(summ: Summary, user_valid=Depends(verify_jwt)):
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
    title = summ.title
    content = summ.content
    user_uid = user_valid.get("sub")
    if not user_uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing supabase uid in token")
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        user_id = await _get_or_create_user_id(conn, user_valid)
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


# ----- GET Methods for frontend Display -----


@router.get("/api/getFlashcardsFromSet")
async def getFlashcardsFromSet(flashset: FlashcardSet, user_valid=Depends(verify_jwt)):
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

        user_uid = user_valid.get("sub")
        if not user_uid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing supabase uid in token")

        user_id = await _get_or_create_user_id(conn, user_valid)

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

        response_content = [dict(row) for row in flashcards]
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


@router.get("/api/getAllFlashcardSets")
async def getAllFlashcardSets(user_valid=Depends(verify_jwt), user_info: User | None = None):
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

        user_uid = user_valid.get("sub")
        if not user_uid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing supabase uid in token")

        user_id = await _get_or_create_user_id(conn, user_valid)

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
        response_content = [dict(row) for row in flashset]

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
