import boto3
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Body
from api.auth import verify_jwt
from pydantic import BaseModel
import asyncpg 
import time
import re
import fitz
import backend.api._retrieveChapters as rc

router = APIRouter()
jobs = {}  # {textbook_id: "processing" | "done"}

# specific bucket
BUCKET = "sg-textbooks"


# create S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION")
)

# s3 = boto3.client("s3")

class ProcessRequest(BaseModel):
    book_id: str
    file_key: str

def upload_file(local_path: str, *, key_prefix: str = "textbooks/uploads") -> str:
    """Upload a local file; key is unique via UUID. key_prefix groups objects (e.g. per textbook)."""
    filename = os.path.basename(local_path) or "file.pdf"
    file_id = str(uuid.uuid4())
    prefix = key_prefix.strip("/")
    key = f"{prefix}/{file_id}-{filename}"

    s3.upload_file(
        local_path,
        BUCKET,
        key,
        ExtraArgs={"ContentType": "application/pdf"},
    )

    # this is the url that will backend needs to send to frontend with a key
    # url = s3.generate_presigned_url(
    #     "put_object",
    #     Params={
    #         "Bucket": BUCKET,
    #         "Key": key,
    #         "ContentType": "application/pdf"
    #     },
    #     ExpiresIn=300
    # )
    # print(url)



    print(f"Uploaded to: {key}")
    return key


def download_file(key: str, download_path: str):
    s3.download_file(
        BUCKET,
        key,
        download_path
    )
    print(f"Downloaded to: {download_path}")


def split_pdf_worker(book_id: str, file_key: str):
    """
    This function runs in the background. It does NOT make the user wait.
    """
    print(f"[{book_id}] Starting background worker for {file_key}...")
    
#     # Step A: Download file from S3 using boto3
#     download_file(file_key, "backend/bookAdders/textbookPDFs/downloaded_textbook.pdf")

    # Step B: Extract chapters path using the improved function from _retrieveChapters.py
    # Return an array --> ["backend/bookAdders/textbookPDFs/chapter1.pdf", "backend/bookAdders/textbookPDFs/chapter2.pdf", ...]
    listOfChapters = rc.extract_chapters_from_pdf_Updated_Better_Version("backend/bookAdders/textbookPDFs/downloaded_textbook.pdf")
    
    # Step D: Upload new files to S3 (processed/book_id/...)
    upload(listOfChapters)
    
    # Step E: Update database status to "Complete"
    
     # Simulating a long 10-second PDF splitting process
    time.sleep(10) 
    
    print(f"[{book_id}] Finished splitting! Uploaded to S3.")


# # my personal path to an existing textbook
# pathToTextbook = "../importFunctionality/textbooks/thinkpython2.pdf"

# # 1. Upload
# file_key = upload_file(pathToTextbook)

# # # 2. Download (test)
# download_file(file_key, "downloaded_textbook.pdf")


"""
Notes: 

1. Set AWS variables aka look at the keys in AWS and put them
in your .env file

2. Add the following env var: AWS_DEFAULT_REGION=us-east-2
"""

# [['The way of the program', [23, 30]], ['Variables, expressions and statements', 
# [31, 38]], ['Functions', [39, 50]], ['Case study: interface design', [51, 60]], 
# ['Conditionals and recursion', [61, 72]], ['Fruitful functions', [73, 84]], ['Iteration', [85, 92]], 
# ['Strings', [93, 104]], ['Case study: word play', [105, 110]], ['Lists', [111, 124]], ['Dictionaries', [125, 136]], 
# ['Tuples', [137, 146]], ['Case study: data structure selection', [147, 158]], ['Files', [159, 168]], ['Classes and objects', 
# [169, 176]], ['Classes and functions', [177, 182]], ['Classes and methods', [183, 192]], 
# ['Inheritance', [193, 204]], ['The Goodies', [205, 214]], ['Debugging', [215, 222]], ['Analysis of Algorithms', [223, 231]]]


# Provides frontend with a presigned url.
@router.post("/api/getPresignedUrl")
async def get_url(user_valid=Depends(verify_jwt)):
    
    supabase_uid = user_valid.get("sub")
    if not supabase_uid:
        raise HTTPException(status_code=401, detail="Missing UID")

    textbook_id = str(uuid.uuid4())
    key = f"textbooks/{textbook_id}"

    conn = None
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )
        status="processing"
        await conn.execute(
            """
            INSERT INTO user_textbook (textbook_id, user_uid, status)
            VALUES ($1, $2, $3)
            ON CONFLICT (textbook_id) DO NOTHING;
            """,
            textbook_id,
            supabase_uid,
            status,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn: await conn.close()
    
    url = s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": BUCKET,
            "Key": key,
            "ContentType": "application/pdf"
        },
        ExpiresIn=3600,
    )
    return {"presigned_url": url, "book_id": textbook_id, "file_key": key}


@router.post("/process-pdf")
async def trigger_pdf_processing(request: ProcessRequest):
    
    # mark job as processing
    jobs[request.book_id] = "processing"

    try:
        print(f"[{request.book_id}] Processing started...")

        # Splits up textbook
        # download_file(request.file_key, "downloaded_textbook.pdf")
        # chapter_map = rc.extract_chapters_from_pdf_Updated_Better_Version("downloaded_textbook.pdf")
        # print(chapter_map)
        
        # simulate work
        time.sleep(10)
        

        print(f"[{request.book_id}] Processing complete.")
        
        conn = None
        try:
            conn = await asyncpg.connect(
                host=os.getenv("DATABASE_HOST"),
                database=os.getenv("DATABASE_NAME"),
                user=os.getenv("DATABASE_USER"),
                password=os.getenv("DATABASE_PASSWORD"),
            )
            await conn.execute(
                """
                UPDATE user_textbook
                SET status = 'complete'
                WHERE textbook_id = $1
                """,
                request.book_id,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if conn: await conn.close()

        # mark job as done
        jobs[request.book_id] = "complete"

        return {
            "message": "Processing completed.",
            "book_id": request.book_id,
            "status": "complete"
        }

    except Exception as e:
        print(f"Error: {e}")
        jobs[request.book_id] = "complete"

        raise HTTPException(status_code=500, detail="Processing failed")


# Uploads chunked chapter PDFs (one batch id per request avoids S3 overwrites on same filenames).
@router.post("/api/uploadTextbookChapters")
async def upload(path_arr: list[str] = Body(...), user_valid=Depends(verify_jwt)):

    uploaded = []
    failed = []

    supabase_uid = user_valid.get("sub")
    if not supabase_uid:
        raise HTTPException(status_code=401, detail="Missing UID")

    upload_batch_id = str(uuid.uuid4())

    for path in path_arr:
        try:
            file_name = Path(path).name or "chapter.pdf"
            s3_key = f"textbooks/{supabase_uid}/{upload_batch_id}/{file_name}"
            s3.upload_file(
                path,
                BUCKET,
                s3_key,
                ExtraArgs={"ContentType": "application/pdf"},
            )
            uploaded.append(s3_key)
        except Exception as e:
            failed.append(path)
            print(f"Error: {e}")

    all_ok = len(failed) == 0
    return {
        "message": "All files uploaded successfully" if all_ok else "Some files failed to upload",
        "upload_batch_id": upload_batch_id,
        "uploaded": uploaded,
        "failed": failed,
    }


@router.get("/api/textbooks/{textbook_id}/status")
async def get_job_status(textbook_id: str):
    conn = None
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )
        row = await conn.fetchrow(
            """
            SELECT status
            FROM user_textbook
            WHERE textbook_id = $1
            """,
            textbook_id,
        )

        if row:
            return {"status": row["status"]}
        raise HTTPException(status_code=404, detail="Textbook not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn: await conn.close()