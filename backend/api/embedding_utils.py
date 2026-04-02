import numpy as np
import torch
import os
import httpx
import asyncpg
import asyncio
from fastapi import HTTPException
from .AIHelper import get_gemini_response
from sentence_transformers import SentenceTransformer
import logging
import uuid

logger = logging.getLogger(__name__)

# load model to keep it in memory
model = SentenceTransformer("all-MiniLM-L6-v2")

# Use MPS if available (Macs), otherwise CPU
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
model = model.to(device)


async def generate_embeddings(texts):
    '''
    This function will asynchronously run the function generate embeddings blocking
    '''
    return await asyncio.to_thread(_generate_embeddings_blocking, texts)


def _generate_embeddings_blocking(texts):
    '''
    This is a blocking function that will generate embeddings for any given text
    using the all-MiniLM-L6-v2 model
    '''
    request_id = str(uuid.uuid4())

    try:
        # Check input type
        if not isinstance(texts, (str, list)):
            raise ValueError("Input must be a string or list of strings.")

        return model.encode(texts)
    
    except Exception as e:
        logger.exception(f"[{request_id}] Error generating embeddings")
        raise RuntimeError(f"Error generating embeddings: {e}") from e

async def generate_Helper(prompt, chapter, textbook):
    '''
    This function will generate embeddings for a prompt then
    run similairity search on a chapters vector embeddings based
    on its textbook 
    '''
    request_id = str(uuid.uuid4())

    # checking for the prompt to be less than or equal to 50 words
    try:
        if len(prompt.split()) > 50:
            raise ValueError("Prompt too long: keep it below 50 words")
    except ValueError as e:
        logger.warning(f"[{request_id}] Invalid request: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    try:
        embedding = await generate_embeddings(prompt)
    except Exception as e:
        raise


    # set embedding to string of float32 values
    embedding = str(np.array(embedding).astype("float32").tolist())

    try:
        logger.info(f"[{request_id}] Connecting to database")

        conn = await asyncpg.connect(
        host=os.getenv("DATABASE_HOST"),
        database=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD")
        )

        logger.info(f"[{request_id}] Retrieving chapter from textbook")

        res = await conn.fetchrow("""
            SELECT c.textbook_id, c.chapter_number
            FROM chapters c
            JOIN textbooks t ON c.textbook_id = t.id
            WHERE t.title = $1 AND c.chapter_title = $2;
        """, textbook, chapter)

        
        if not res:
            logger.warning(f"[{request_id}] Chapter or textbook not found")

            raise HTTPException(
                status_code=404,
                detail=f"Chapter {chapter} not found or textbook {textbook} not found.")


        textbook_id = res["textbook_id"]
        chapter_number = res["chapter_number"]

        logger.info(f"[{request_id}] Fetching chunks")

        rows = await conn.fetch("""
            SELECT chunk_text, embedding <-> $1 AS distance
            FROM chapter_embeddings
            WHERE textbook_id = $2 AND chapter_number = $3
            ORDER BY distance ASC
            LIMIT 1;
        """, embedding, textbook_id, chapter_number)

        if not rows:
            logger.warning(f"[{request_id}] No chunks found")

            raise HTTPException(
                status_code=404,
                detail=f"Empty Table Row")
        
        # combine context and make a prompt
        context = "\n".join(row[0] for row in rows)
        prompt = f"Context:\n{context}\n\nQuestion: {prompt}\nAnswer: Provide a concise response\nIf no similiar content then respond with: No Context Applies"


        try:
            logger.info(f"[{request_id}] Sending prompt to LLM")
            answer = await get_gemini_response(prompt)

        except HTTPException:
            raise

        except Exception:
            logger.exception(f"[{request_id}] Model Generation Error")
            raise HTTPException(status_code=500, detail="Model Generation Error.")

        return answer
    
    except ValueError:
        raise 
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[{request_id}] Database error")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        await conn.close()


