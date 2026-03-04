from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
# from .embedding_utils import getModelResponse
import os 
import asyncpg
import random
from fastapi import status
from fastapi.responses import JSONResponse
from .openAIHelper import get_openai_response

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
async def generate_endpoint(request: FlashRequest):
    '''
    This endpoint will generate a x amount of flashcards.
    It will return flashcards in a map of cards that contain
    a question and an answer
    '''

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

    print(chapter)
    print(textbook)
    print(count)
    print("\n\n")

    # Validate inputs first.
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

        print(chunkCount)


        if chunkCount <= 0:
            raise HTTPException(status_code=404, detail="No text chunks found for the given chapter.")

        # if request more than available chunks
        if count > chunkCount:
            count = chunkCount
        print("-------------------------------------")
        print(f"There is a Chunk total of {chunkCount}")
        print(f"There is a Count total of {count}\n\n")

        question_answer_pair = {}
        selectedChunks = set()

        latencyTime = []
        throughPutStartTime = time.time()
        for c in range(count):
            latencyStartTime = time.time()

            # generate a random number between 1 and chunk count
            while True:
                random_chunk = random.randint(1, chunkCount)
                if random_chunk not in selectedChunks:
                    selectedChunks.add(random_chunk)
                    break 

            
            print(f'This is the chunk: {random_chunk}')
            print(f'This is the count: {c}')


            # Retrieve Random chunk
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

                
                    # Validate both fields
                    if not question or not answer:
                        continue
                    

                    question_answer_pair[f"Question {c}"] = (question, answer)

            except Exception as e:
                continue

            # flashcard has been generated
            latencyTime.append(round(time.time() - latencyStartTime, 4))
            
        
        if not question_answer_pair:
            print("Here")
            raise HTTPException(status_code=422, detail="No valid flashcards were generated.")

        #set log values for perf teting
        status_code = 200
        cards_returned = len(question_answer_pair)

        # Cards are completed
        throughput = round(count / (time.time() - throughPutStartTime), 4)
        #test print
        print("Latency List: ", latencyTime)
        print("Throughput: ", throughput)
        # send write these results to a different csv file
        """
        latency CSV
        throughput CSV
        
        Prep: Print out if the times code I just wrote worked
        1. Read a csv using pandas
        2. Fill out the columns that will be Latency
        2. FIll out the columns that will be throughput 
        3. Run your previous file that you wrote to activate multiple test
        """


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
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        #compute elapsed time
        elapsed_time = round(time.perf_counter() - request_start, 4)

        #building throughput CSV
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

        fieldnames = [
            "timestamp",
            "endpoint",
            "textbook",
            "chapter",
            "requested_count",
            "status_code",
            "cards_returned",
            "throughput",
            "error",
        ]

        os.makedirs(os.path.dirname(throughput_csv_path), exist_ok=True)
        file_exists = os.path.exists(throughput_csv_path)
        file_empty = (not file_exists) or os.path.getsize(throughput_csv_path) == 0
        
        with open(throughput_csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if file_empty:
                writer.writeheader()
            writer.writerow(row)
        
        #building latency stats CSV
        row = {
            "textbook": textbook,
            "chapter": chapter,
            "cards_returned": cards_returned,
            "latency_time": latencyTime
        }

        fieldnames = [
            "textbook",
            "chapter",
            "cards_returned",
            "latency_time",
        ]

        os.makedirs(os.path.dirname(latency_csv_path), exist_ok=True)
        file_exists = os.path.exists(latency_csv_path)
        file_empty = (not file_exists) or os.path.getsize(latency_csv_path) == 0
        
        with open(latency_csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if file_empty:
                writer.writeheader()
            writer.writerow(row)

        await conn.close()