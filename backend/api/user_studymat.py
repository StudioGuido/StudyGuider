from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import asyncpg
from typing import List
from api.auth import verify_jwt

router = APIRouter()


# ---------------- MODELS ---------------- #

class FlashcardSet(BaseModel):
    title: str


class Flashcard(BaseModel):
    question: str
    answer: str
    textbook_id: int
    chapter_number: int
    chunk_index: int


class AssignFlashcard(BaseModel):
    set_title: str
    flashcard_id: int


class Summary(BaseModel):
    title: str
    content: str


# ---------------- FLASHCARD SET ---------------- #

@router.post("/api/createFlashCardSet")
async def create_flashcard_set(
    flashset: FlashcardSet,
    user_valid=Depends(verify_jwt)
):
    conn = None
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        user_id = user_valid.get("sub")
        if not user_id:
            raise HTTPException(401, "Missing UID")

        row = await conn.fetchrow(
            """
            INSERT INTO flash_card_set (set_title, user_id)
            VALUES ($1, $2)
            RETURNING fcset_id, set_title
            """,
            flashset.title,
            user_id,
        )

        return JSONResponse(status_code=201, content={"response": dict(row)})

    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(400, "Flashcard set already exists")

    except Exception as e:
        raise HTTPException(500, str(e))

    finally:
        if conn:
            await conn.close()
            
@router.put("/api/updateFlashcardSetName")
async def update_flashcard_set_name(
    old_title: str,
    new_title: str,
    user_valid=Depends(verify_jwt)
):
    conn = None
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        user_id = user_valid.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Missing UID")

        result = await conn.execute(
            """
            UPDATE flash_card_set
            SET set_title = $1
            WHERE user_id = $2 AND set_title = $3
            """,
            new_title,
            user_id,
            old_title,
        )

        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Flashcard set not found")

        return {"message": "Flashcard set name updated successfully"}

    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(
            status_code=400,
            detail="A flashcard set with this name already exists"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if conn:
            await conn.close()


@router.delete("/api/deleteFlashSet")
async def delete_flashcard_set(
    flashset: FlashcardSet,
    user_valid=Depends(verify_jwt)
):
    conn = None
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        user_id = user_valid.get("sub")
        if not user_id:
            raise HTTPException(401, "Missing UID")

        result = await conn.execute(
            """
            DELETE FROM flash_card_set
            WHERE user_id = $1 AND set_title = $2
            """,
            user_id,
            flashset.title,
        )

        if result == "DELETE 0":
            raise HTTPException(404, "Flash set not found")

        return {"message": "Flash set deleted successfully"}

    except Exception as e:
        raise HTTPException(500, str(e))

    finally:
        if conn:
            await conn.close()


@router.get("/api/getAllFlashcardSets")
async def get_all_flashcard_sets(user_valid=Depends(verify_jwt)):
    conn = None
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        user_id = user_valid.get("sub")
        if not user_id:
            raise HTTPException(401, "Missing UID")

        rows = await conn.fetch(
            """
            SELECT fcset_id, set_title
            FROM flash_card_set
            WHERE user_id = $1
            """,
            user_id,
        )

        return {"response": [dict(r) for r in rows]}

    except Exception as e:
        raise HTTPException(500, str(e))

    finally:
        if conn:
            await conn.close()


# ---------------- MASTER FLASHCARD ---------------- #

@router.post("/api/addMasterFlashcard")
async def add_master_flashcard(
    flashcard: Flashcard,
    user_valid=Depends(verify_jwt)
):
    conn = None
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        user_id = user_valid.get("sub")
        if not user_id:
            raise HTTPException(401, "Missing UID")

        row = await conn.fetchrow(
            """
            INSERT INTO master_flashcard
            (question, answer, textbook_id, chapter_number, chunk_index)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING fc_id, question, answer, textbook_id, chapter_number, chunk_index
            """,
            flashcard.question,
            flashcard.answer,
            flashcard.textbook_id,
            flashcard.chapter_number,
            flashcard.chunk_index,
        )

        return JSONResponse(status_code=201, content={"response": dict(row)})

    except Exception as e:
        raise HTTPException(500, str(e))

    finally:
        if conn:
            await conn.close()


# ---------------- ASSIGN / REMOVE FLASHCARDS ---------------- #

@router.post("/api/addFlashcardToSet")
async def add_flashcard_to_set(
    data: AssignFlashcard,
    user_valid=Depends(verify_jwt)
):
    conn = None
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        user_id = user_valid.get("sub")

        fcset = await conn.fetchrow(
            """
            SELECT fcset_id FROM flash_card_set
            WHERE user_id = $1 AND set_title = $2
            """,
            user_id,
            data.set_title,
        )

        if not fcset:
            raise HTTPException(404, "Flashcard set not found")

        await conn.execute(
            """
            INSERT INTO flash_card_set_assignment (fcset_id, master_fc_id)
            VALUES ($1, $2)
            ON CONFLICT DO NOTHING
            """,
            fcset["fcset_id"],
            data.flashcard_id,
        )

        return {"message": "Flashcard added to set"}

    except Exception as e:
        raise HTTPException(500, str(e))

    finally:
        if conn:
            await conn.close()


@router.delete("/api/removeFlashcardFromSet")
async def remove_flashcard_from_set(
    data: AssignFlashcard,
    user_valid=Depends(verify_jwt)
):
    conn = None
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        user_id = user_valid.get("sub")

        fcset = await conn.fetchrow(
            """
            SELECT fcset_id FROM flash_card_set
            WHERE user_id = $1 AND set_title = $2
            """,
            user_id,
            data.set_title,
        )

        if not fcset:
            raise HTTPException(404, "Flashcard set not found")

        result = await conn.execute(
            """
            DELETE FROM flash_card_set_assignment
            WHERE fcset_id = $1 AND master_fc_id = $2
            """,
            fcset["fcset_id"],
            data.flashcard_id,
        )

        if result == "DELETE 0":
            raise HTTPException(404, "Flashcard not in set")

        return {"message": "Flashcard removed from set"}

    except Exception as e:
        raise HTTPException(500, str(e))

    finally:
        if conn:
            await conn.close()


# ---------------- GET FLASHCARDS ---------------- #

@router.get("/api/getFlashcardsFromSet")
async def get_flashcards_from_set(
    title: str,
    user_valid=Depends(verify_jwt)
):
    conn = None
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        user_id = user_valid.get("sub")

        rows = await conn.fetch(
            """
            SELECT mf.fc_id, mf.question, mf.answer
            FROM flash_card_set fcs
            JOIN flash_card_set_assignment fsa ON fcs.fcset_id = fsa.fcset_id
            JOIN master_flashcard mf ON fsa.master_fc_id = mf.fc_id
            WHERE fcs.user_id = $1 AND fcs.set_title = $2
            """,
            user_id,
            title,
        )

        return {"response": [dict(r) for r in rows]}

    except Exception as e:
        raise HTTPException(500, str(e))

    finally:
        if conn:
            await conn.close()


# ---------------- SEEN FLASHCARDS ---------------- #

@router.post("/api/markFlashcardSeen")
async def mark_flashcard_seen(
    flashcard_id: int,
    user_valid=Depends(verify_jwt)
):
    conn = None
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        user_id = user_valid.get("sub")

        await conn.execute(
            """
            INSERT INTO seen_card (user_id, flashcard_id)
            VALUES ($1, $2)
            ON CONFLICT DO NOTHING
            """,
            user_id,
            flashcard_id,
        )

        return {"message": "Marked as seen"}

    except Exception as e:
        raise HTTPException(500, str(e))

    finally:
        if conn:
            await conn.close()


@router.get("/api/getSeenFlashcards")
async def get_seen_flashcards(user_valid=Depends(verify_jwt)):
    conn = None
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        user_id = user_valid.get("sub")

        rows = await conn.fetch(
            """
            SELECT mf.fc_id, mf.question, mf.answer
            FROM seen_card sc
            JOIN master_flashcard mf ON sc.flashcard_id = mf.fc_id
            WHERE sc.user_id = $1
            """,
            user_id,
        )

        return {"response": [dict(r) for r in rows]}

    except Exception as e:
        raise HTTPException(500, str(e))

    finally:
        if conn:
            await conn.close()


# ---------------- SUMMARY ---------------- #

@router.post("/api/saveSummary")
async def save_summary(
    summ: Summary,
    user_valid=Depends(verify_jwt)
):
    conn = None
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        user_id = user_valid.get("sub")

        row = await conn.fetchrow(
            """
            INSERT INTO summary (user_id, title, content)
            VALUES ($1, $2, $3)
            RETURNING summary_id, title, content
            """,
            user_id,
            summ.title,
            summ.content,
        )

        return JSONResponse(status_code=201, content={"response": dict(row)})

    except Exception as e:
        raise HTTPException(500, str(e))

    finally:
        if conn:
            await conn.close()
            
@router.get("/api/getSummaries")
async def get_summaries(user_valid=Depends(verify_jwt)):
    conn = None
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        user_id = user_valid.get("sub")
        if not user_id:
            raise HTTPException(401, "Missing UID")

        rows = await conn.fetch(
            """
            SELECT summary_id, title, content
            FROM summary
            WHERE user_id = $1
            ORDER BY summary_id DESC
            """,
            user_id,
        )

        return {"response": [dict(r) for r in rows]}

    except Exception as e:
        raise HTTPException(500, str(e))

    finally:
        if conn:
            await conn.close()
            
@router.delete("/api/deleteSummary/{summary_id}")
async def delete_summary(summary_id: int, user_valid=Depends(verify_jwt)):
    conn = None
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        user_id = user_valid.get("sub")
        if not user_id:
            raise HTTPException(401, "Missing UID")

        result = await conn.execute(
            """
            DELETE FROM summary
            WHERE user_id = $1 AND summary_id = $2
            """,
            user_id,
            summary_id,
        )

        if result == "DELETE 0":
            raise HTTPException(404, "Summary not found")

        return {"message": "Summary deleted successfully"}

    except Exception as e:
        raise HTTPException(500, str(e))

    finally:
        if conn:
            await conn.close()