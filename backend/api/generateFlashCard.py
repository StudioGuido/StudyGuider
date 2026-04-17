from datetime import datetime

from api.auth import verify_jwt
from fastapi import APIRouter, HTTPException, Request
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import os 
import asyncpg
import random
from fastapi import status
from fastapi.responses import JSONResponse
from .openAIHelper import get_openai_response
# import asyncio 
# from contextlib import asynccontextmanager 


#for perf testing
import csv
import time


latency_csv_path="api/latency.csv"
throughput_csv_path="api/throughput.csv"

router = APIRouter()

class FlashRequest(BaseModel):
    textbook: str
    chapter: str
    count: int


@router.post("/api/generateFlashCard")
async def generate_endpoint(request: FlashRequest ):  #user validation didn't go through (are we passing the user id as a jwt token??)
    '''
    This endpoint will generate a x amount of flashcards.
    It will return flashcards in a map of cards that contain
    a question and an answer
    '''
    # user_id = user_valid.get("sub")  # Assuming the user ID is stored in the sub claim of the JWT?

    user_id = '1'  # Placeholder user ID for testing purposes. Replace later
    chapter = request.chapter
    textbook = request.textbook
    count = request.count
    

    #Start the timer for performance testing
    request_start = time.perf_counter()

    #initialize log variables for perf testing
    status_code = None
    cards_returned = 0
    error = ""
    requested_count = request.count
    throughput = 0
    latencyTime = []
    throughPutStartTime = time.time()  # initialize here so it's always defined

    print(chapter)
    print(textbook)
    print(count)
    print("\n\n")

    # Validate inputs first.

    #user validation

    if not textbook or not chapter or count <= 0:
        raise HTTPException(status_code=400, detail="Invalid textbook or chapter title")

    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to connect to database.")
        
    try: #just for now 
        await conn.execute("""
            INSERT INTO users(supabase_uid)
            VALUES ($1)
            ON CONFLICT (supabase_uid) DO NOTHING
        """, user_id)

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
        #filters only for this current user from the master flashcard table 
        existing_flashcards = await conn.fetch("""
            SELECT fc_id, question, answer, chunk_index
            FROM master_flashcard
            WHERE textbook_id = $1 AND chapter_number = $2 AND user_id = $3 AND last_seen < NOW() - INTERVAL '1 minute'
            ORDER BY last_seen ASC
            LIMIT $4
            
        """, textbook_id, chapter_number, user_id, count)
#larger values means it was just seen so we want to order by ascending last_seen so we get the flashcards that werent seen for a while

        print(f"Existing flashcards found: {len(existing_flashcards)}")

        question_answer_pair = {}
        seen_ids = []

        for i, row in enumerate(existing_flashcards):
            if len(question_answer_pair) >= count:
                break
            question_answer_pair[f"Question {i}"] = (row["question"], row["answer"])
            print(question_answer_pair)
            seen_ids.append(row["fc_id"])

        if seen_ids: 
            await conn.execute(""" 
                UPDATE master_flashcard SET last_seen = NOW()
                WHERE fc_id = ANY($1::int[])                       
                                """, seen_ids)
        if len(question_answer_pair) < count:
            chunkCount = await conn.fetchrow("""
                SELECT COUNT(*) 
                FROM chapter_embeddings 
                WHERE textbook_id = $1 AND chapter_number = $2;
            """, textbook_id, chapter_number)

            chunkCount = int(chunkCount['count'])
            print(chunkCount)

            if chunkCount <= 0:
                raise HTTPException(status_code=404, detail="No text chunks found for the given chapter.")

            if count > chunkCount:
                count = chunkCount

            print("-------------------------------------")
            print(f"There is a Chunk total of {chunkCount}")
            print(f"There is a Count total of {count}\n\n")

            question_answer_pair = {}
            selectedChunks = set()
            throughPutStartTime = time.time()

            for c in range(count):
                latencyStartTime = time.time()

                while True:
                    random_chunk = random.randint(1, chunkCount)
                    if random_chunk not in selectedChunks:
                        selectedChunks.add(random_chunk)
                        break

                print(f'This is the chunk: {random_chunk}')
                print(f'This is the count: {c}')

                chunk = await conn.fetchrow("""
                    SELECT chunk_text
                    FROM chapter_embeddings
                    WHERE textbook_id = $1 AND chapter_number = $2 AND chunk_index = $3;
                """, textbook_id, chapter_number, random_chunk)

                print(chunk)

                if chunk is None:
                    continue

                prompt = f"Context: {chunk}\nCreate a question using the context and provide an answer to the question.\
                    Format:\nQuestion:\nAnswer:"

                try:
                    print("Generating...........\n\n")
                    modelResponse = await get_openai_response(prompt)
                except Exception as e:
                    continue

                try:
                    if "Answer:" in modelResponse:
                        question, answer = modelResponse.split("Answer:", 1)
                        question = question.strip()
                        question = question.replace("Question:", "").strip().rstrip("?")
                        answer = answer.strip()

                        if not question or not answer:
                            continue

                        try:
                    
                            # Insert into seen_card table
                            fc_id = await conn.fetchval("""
                                INSERT INTO master_flashcard(textbook_id, chapter_number, question, answer, chunk_index, user_id)
                                VALUES ($1, $2, $3, $4, $5, $6)
                                RETURNING fc_id
                            """, textbook_id, chapter_number, question, answer, random_chunk, user_id)

                            await conn.execute("""
                                INSERT INTO seen_card(user_id, flashcard_id)
                                VALUES ($1, $2)
                                ON CONFLICT DO NOTHING
                            """, user_id, fc_id)
                        except Exception as e:
                            print("unable to populate master table or seen table", str(e))
                        else:
                            print(f"INSERTED FLASHCARD: {question[0:50]}...into master_flashcard")
                            question_answer_pair[f"Question {c}"] = (question, answer)

                except Exception as e:
                    continue

                latencyTime.append((time.time() - latencyStartTime))

        if not question_answer_pair:
            print("Here")
            raise HTTPException(status_code=422, detail="No valid flashcards were generated.")

        status_code = 200
        cards_returned = len(question_answer_pair)
        throughput = (count / (time.time() - throughPutStartTime))

        print("Latency List: ", latencyTime)
        print("Throughput: ", throughput)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"response": question_answer_pair}
        )
    
        

    except HTTPException as e:
        status_code = e.status_code
        error = str(e.detail) if e.detail is not None else str(e)
        raise
    except Exception as e:
        status_code = 500
        error = str(e)
        print("TOP LEVEL ERROR:", str(e))  # add this line
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        elapsed_time = round(time.perf_counter() - request_start, 4)

        row = {
            "timestamp": int(time.time()),
            "endpoint": "/api/generateFlashCard",
            "textbook": textbook,
            "chapter": chapter,
            "requested_count": requested_count,
            "status_code": status_code if status_code is not None else "",
            "cards_returned": cards_returned,
            "throughput": throughput,
            "error": error,
        }

        fieldnames = ["timestamp", "endpoint", "textbook", "chapter", "requested_count", "status_code", "cards_returned", "throughput", "error"]

        os.makedirs(os.path.dirname(throughput_csv_path), exist_ok=True)
        file_exists = os.path.exists(throughput_csv_path)
        file_empty = (not file_exists) or os.path.getsize(throughput_csv_path) == 0

        with open(throughput_csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if file_empty:
                writer.writeheader()
            writer.writerow(row)

        row = {
            "textbook": textbook,
            "chapter": chapter,
            "cards_returned": cards_returned,
            "latency_time": latencyTime
        }

        fieldnames = ["textbook", "chapter", "cards_returned", "latency_time"]

        os.makedirs(os.path.dirname(latency_csv_path), exist_ok=True)
        file_exists = os.path.exists(latency_csv_path)
        file_empty = (not file_exists) or os.path.getsize(latency_csv_path) == 0

        with open(latency_csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if file_empty:
                writer.writeheader()
            writer.writerow(row)

        await conn.close()


