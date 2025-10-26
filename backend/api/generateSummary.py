from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import os 
import asyncpg
from fastapi import status
from fastapi.responses import JSONResponse
import re

from .openAIHelper import get_openai_response

router = APIRouter()

class SummaryRequest(BaseModel):
    textbook: str
    chapter: str
'''
Defines the structure of the user request for chapter summaries:
- textbook: title of the textbook
- chapter: title of the chapter
'''

@router.post("/api/generateSummary")
async def generate_endpoint(request: SummaryRequest):

    chapter = request.chapter
    textbook = request.textbook

    try:
        conn = await asyncpg.connect(
        host=os.getenv("DATABASE_HOST"),
        database=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD")
        )
    

        # Fetch chapter information
        res = await conn.fetchrow("""
            SELECT c.textbook_id, c.chapter_number
            FROM chapters c
            JOIN textbooks t ON c.textbook_id = t.id
            WHERE t.title = $1 AND c.chapter_title = $2;
        """, textbook, chapter)

        if res == None:
            raise HTTPException(status_code=400, detail="Invalid textbook or chapter title")

        
        textbook_id = res["textbook_id"]
        chapter_number = res["chapter_number"]

        # Fetch all chunks for the chapter
        all_chunk = await conn.fetch("""
        SELECT chunk_text 
        FROM chapter_embeddings 
        WHERE textbook_id = $1 AND chapter_number = $2;
        """, textbook_id, chapter_number)

        if all_chunk == None:
            raise HTTPException(status_code=404, detail="No chunks from in database")
        
        # Helper function to clean a single chunk
        def clean_chunk(text):
            text = text.strip()
            text = re.sub(r"\n+", " ", text)
            return text

        # Flatten + clean all chunks & combine into one big text blob
        chapter_text = " ".join(
            clean_chunk(row["chunk_text"])
            for row in all_chunk
            if row["chunk_text"].strip()
        )

        # Build the OpenAI prompt
        prompt = f"""
        Summarize the following chapter so that a student can easily understand the main ideas, key concepts, and important details. Use clear and simple language.

        Chapter Content:
        {chapter_text}
        """
        # Call OpenAI asynchronously
        try:
            modelResponse = await get_openai_response(prompt)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")


        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"response": modelResponse}
        )
    
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        await conn.close()
'''
    Endpoint to generate a chapter summary using OpenAI.
    
    1. Extract textbook and chapter from the user request.
    2. Connect asynchronously to PostgreSQL and fetch chapter info.
    3. Fetch all text chunks for the chapter.
    4. Clean and combine all chunks into a single text string.
    5. Build a prompt and call OpenAI asynchronously.
    6. Return the summary as JSON.

    Raises:
    - HTTPException(400) if the textbook or chapter is invalid.
    - HTTPException(404) if no chunks are found in the database.
    - HTTPException(500) for database or OpenAI API errors.
    '''

'''
Library:
- fastapi: builds APIs, handles requests, routes, and HTTP responses
- pydantic: data validation and JSON-to-Python conversion
- os: access environment variables securely
- asyncpg: asynchronous PostgreSQL so queries aren't blocked from running
- status: readable HTTP status codes
- JSONResponse: sends Python data as JSON to the frontend
- re: regular expressions for text cleaning
- openAIHelper.get_openai_response: async OpenAI call for generating summaries
'''