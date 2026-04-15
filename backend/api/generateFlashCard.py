from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
# from .embedding_utils import getModelResponse
import os 
import asyncpg
import random
from fastapi import status
from fastapi.responses import JSONResponse
from .AIHelper import get_gemini_response
import logging
import uuid

router = APIRouter()
logger = logging.getLogger(__name__)

class FlashRequest(BaseModel):
    textbook: str
    chapter: str
    count: int


@router.post("/api/generateFlashCard")
async def generate_endpoint(request: FlashRequest):
    '''
    This endpoint will generate a x amount of flashcards.
    It will return flashcards in a map of cards that contain
    a question and an answer
    '''
    request_id = str(uuid.uuid4())

    chapter = request.chapter
    textbook = request.textbook
    count = request.count

    logger.info(f"[{request_id}] Textbook: {textbook} Chapter: {chapter} Count: {count}")

    # Validate inputs first.
    if not textbook or not chapter or count <= 0:
        raise HTTPException(status_code=400, detail="Invalid textbook or chapter title")

    try:
        logger.info(f"[{request_id}] Connecting to database")

        conn = await asyncpg.connect(
        host=os.getenv("DATABASE_HOST"),
        database=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD")
        )
    except Exception as e:
        logger.exception(f"[{request_id}] Failed to connect to database")
        raise HTTPException(status_code=500, detail="Failed to connect to database.")

    try:
        # Gather chapter from textbook
        res = await conn.fetchrow("""
            SELECT c.textbook_id, c.chapter_number
            FROM chapters c
            JOIN textbooks t ON c.textbook_id = t.id
            WHERE t.title = $1 AND c.chapter_title = $2;
        """, textbook, chapter)



        if res == None:
            raise HTTPException(status_code=400, detail="Invalid textbook or chapter name")


        # Extract the amount of chunks in the chapter
        textbook_id = res["textbook_id"]
        chapter_number = res["chapter_number"]

        chunkCount = await conn.fetchrow("""
        SELECT COUNT(*) 
        FROM chapter_embeddings 
        WHERE textbook_id = $1 AND chapter_number = $2;
        """, textbook_id, chapter_number)



        chunkCount = int(chunkCount['count'])

        if chunkCount <= 0:
            raise HTTPException(status_code=404, detail="No text chunks found for the given chapter.")

        # if request more than available chunks
        if count > chunkCount:
            count = chunkCount
        
        logger.info(f"[{request_id}] Chunk total: {chunkCount}")
        logger.info(f"[{request_id}] Requested count total: {count}")

        question_answer_pair = {}
        selectedChunks = set()
        error_count = 0
        for c in range(count):

            # generate a random number between 1 and chunk count
            while True:
                random_chunk = random.randint(1, chunkCount)
                if random_chunk not in selectedChunks:
                    selectedChunks.add(random_chunk)
                    break 

            logger.info(f"[{request_id}] Getting random chunk")

            # Retrieve Random chunk
            chunk = await conn.fetchrow("""
            SELECT chunk_text
            FROM chapter_embeddings
            WHERE textbook_id = $1 AND chapter_number = $2 AND chunk_index = $3;
            """, textbook_id, chapter_number, random_chunk)

            logger.info(f"[{request_id}] Retrieved chunk index: {random_chunk}")

            if chunk is None:
                continue


            prompt = f"Context: {chunk}\nCreate a question using the context and provide an answer to the question.\
                Format:\nQuestion:\nAnswer:"
        
            
            try:
                logger.info(f"[{request_id}] Generating...")

                modelResponse = await get_gemini_response(prompt)
            except Exception as e:
                error_count += 1
                if error_count >= 6:
                    logger.error(f"[{request_id}] Too many LLM failures ({error_count}), stopping early at card {c}/{count}")
                    break
                continue

            
            try:
                if "Answer:" in modelResponse:
                    question, answer = modelResponse.split("Answer:", 1)
                    question = question.strip()
                    question = question.replace("Question:", "").strip().rstrip("?")
                    answer = answer.strip()
                
                    # Validate both fields
                    if not question or not answer:
                        continue
                    

                    question_answer_pair[f"Question {c}"] = (question, answer)

            except Exception as e:
                logger.warning(f"[{request_id}] Failed to parse model {e}")
                continue
            
        
        if not question_answer_pair:
            logger.warning(f"[{request_id}] No valid flashcards are generated.")
            raise HTTPException(status_code=422, detail="No valid flashcards were generated.")


        return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"response": question_answer_pair}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[{request_id}] Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        await conn.close()