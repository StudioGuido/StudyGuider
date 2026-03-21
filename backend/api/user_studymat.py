from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import os
import asyncpg
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from api.auth import verify_jwt

router = APIRouter()


class FlashcardSet(BaseModel):
    title: str


class MasterFlashcardCreate(BaseModel):
    """Body for inserting one row into `master_flashcard` (canonical Q/A + chunk FK)."""

    question: str
    answer: str
    textbook_id: int
    chapter_number: int
    chunk_index: int


class Flashcard(BaseModel):
    """Assign an existing master flashcard into a user set."""

    flashcardset: FlashcardSet
    master_fc_id: int


class Summary(BaseModel):
    title: str
    content: str


async def get_valid_user(conn: asyncpg.Connection, user_valid: dict) -> str:
    """
    Resolve and validate app user from Supabase JWT `sub`.
    Raises if token is missing `sub` or user row does not exist.
    """
    user_uid = user_valid.get("sub")
    if not user_uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing supabase uid in token")

    user = await conn.fetchrow(
        "SELECT supabase_uid FROM users WHERE supabase_uid = $1",
        user_uid,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User has not been created",
        )
    return str(user["supabase_uid"])


@router.post("/api/createMasterFlashcard")
async def create_master_flashcard(body: MasterFlashcardCreate, user_valid=Depends(verify_jwt)):
    """Insert a single row into `master_flashcard`. Use `/api/addToFlashCardSet` to put it in a set."""
    conn = None
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )
        await get_valid_user(conn, user_valid)

        try:
            row = await conn.fetchrow(
                """
                INSERT INTO master_flashcard
                    (question, answer, textbook_id, chapter_number, chunk_index)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING fc_id, question, answer, textbook_id, chapter_number, chunk_index
                """,
                body.question,
                body.answer,
                body.textbook_id,
                body.chapter_number,
                body.chunk_index,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating master flashcard: {e}")

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder({"response": dict(row)}),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn:
            await conn.close()


@router.post("/api/createFlashCardSet")
async def create_flashcard_set(flashset: FlashcardSet, user_valid=Depends(verify_jwt)):
    """
    API Endpoint for flash card set creation

    Creates a flashcard set scoped to the authenticated user.
    """
    title = flashset.title
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )
        print("""User validation payload in create_flashcard_set:""")
        print(user_valid)
        user_id = await get_valid_user(conn, user_valid)

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
async def delete_flashcard_set(flashset: FlashcardSet, user_valid=Depends(verify_jwt)):
    """Delete a flashcard set owned by the authenticated user."""
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        user_id = await get_valid_user(conn, user_valid)

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
async def update_flashcard_set(update_title: str, flashset: FlashcardSet, user_valid=Depends(verify_jwt)):
    """Update the title of a flashcard set owned by the authenticated user."""
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )
        user_id = await get_valid_user(conn, user_valid)

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
    Link existing `master_flashcard` rows (by `master_fc_id`) into a user flashcard set.
    Create masters first via `/api/createMasterFlashcard`.
    """
    set_title = flashcards[0].flashcardset.title
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )
        user_id = await get_valid_user(conn, user_valid)

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
        added: List[Dict[str, Any]] = []
        try:
            for flashcard in flashcards:
                row = await conn.fetchrow(
                    """
                    INSERT INTO flash_card_set_assignment (fcset_id, master_fc_id)
                    VALUES ($1, $2)
                    ON CONFLICT (fcset_id, master_fc_id) DO NOTHING
                    RETURNING fcset_id, master_fc_id
                    """,
                    fcset_id,
                    flashcard.master_fc_id,
                )
                if row:
                    added.append(dict(row))

        except Exception as e:
            raise HTTPException(500, f"Error in making flashcard: {e}")

        try:
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content=jsonable_encoder({"response": added}),
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

    Saves an input summary to the authenticated user.
    """
    title = summ.title
    content = summ.content
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        user_id = await get_valid_user(conn, user_valid)
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

    Returns all flashcards for one set belonging to the authenticated user.
    """
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        user_id = await get_valid_user(conn, user_valid)

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
            SELECT
                fcsa.fcset_id,
                fcsa.master_fc_id,
                mf.question,
                mf.answer,
                mf.textbook_id,
                mf.chapter_number,
                mf.chunk_index
            FROM flash_card_set_assignment AS fcsa
            INNER JOIN master_flashcard AS mf ON mf.fc_id = fcsa.master_fc_id
            WHERE fcsa.fcset_id = $1
            ORDER BY fcsa.master_fc_id
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
async def getAllFlashcardSets(user_valid=Depends(verify_jwt)):
    """
    API Endpoint for getting all Flashcard Sets

    Returns all flashcard sets for the authenticated user.
    """
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        user_id = await get_valid_user(conn, user_valid)

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
