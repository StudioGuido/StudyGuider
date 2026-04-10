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
import api._retrieveChapters as rc

"""
Notes: 

1. Set AWS variables aka look at the keys in AWS and put them
in your .env file

2. Add the following env var: AWS_DEFAULT_REGION=us-east-2
"""


router = APIRouter()

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
    print(f"Uploaded to: {key}")
    return key

# Uploads chunked chapter PDFs (one batch id per request avoids S3 overwrites on same filenames).
async def upload(supabase_uid, path_arr, textbook_id):
    uploaded = []
    failed = []

    upload_batch_id = str(uuid.uuid4())
    print("5", path_arr)
    
    conn = None
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )
        
        # Iterates over paths, uploading them to s3 and postgre db
        chapter_count = 1
        for path in path_arr:
            print("6", path)
            try:
                # Generates chapter id and insert chapter into the db
                chapter_id = str(uuid.uuid4())
                await conn.execute(
                    """
                    INSERT INTO textbook_chapter (chapter_id, textbook_id)
                    VALUES ($1, $2)
                    ON CONFLICT (chapter_id, textbook_id) DO NOTHING;
                    """,
                    chapter_count,
                    textbook_id,
                )
                chapter_count+=1
                
                # chapter_name = Path(path).name or "chapter.pdf"
                # s3_key = f"textbooks/{supabase_uid}/{upload_batch_id}/{file_name}"
                local_file_path = Path(path)
                print(local_file_path.parts)
                s3_key = f"users/{supabase_uid}/textbooks/{textbook_id}/chapters/{chapter_count}"
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
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn: await conn.close()
    
    all_ok = len(failed) == 0
    return {
        "message": "All files uploaded successfully" if all_ok else "Some files failed to upload",
        "upload_batch_id": upload_batch_id,
        "uploaded": uploaded,
        "failed": failed,
    }

def download_file(key: str, download_path: str):
    s3.download_file(
        BUCKET,
        key,
        download_path
    )
    print(f"Downloaded to: {download_path}")

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
async def trigger_pdf_processing(request: ProcessRequest, user_valid=Depends(verify_jwt)):
    
    supabase_uid = user_valid.get("sub")
    if not supabase_uid:
        raise HTTPException(status_code=401, detail="Missing UID")

    try:
        print(f"[{request.book_id}] Processing started...")

        # downloads file from s3 (uploaded to via frontend)
        download_file(request.file_key, "downloaded_textbook.pdf")
        
        # Generates list of local downloaded chapter paths
        listOfChapters, textbook_title = rc.extract_chapters_from_pdf_Updated_Better_Version("downloaded_textbook.pdf", supabase_uid)


        # creates keys from filepaths and uploads chunks to s3
        await upload(supabase_uid, listOfChapters, request.book_id)
        

        print(f"[{request.book_id}] Processing complete.")
        # Update db
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
                WHERE textbook_id = $1 AND textbook_title = $2
                """,
                request.book_id,
                textbook_title,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if conn: await conn.close()

        return {
            "message": "Processing completed.",
            "book_id": request.book_id,
            "status": "complete"
        }

    except Exception as e:
        print(f"Error: {e}")

        raise HTTPException(status_code=500, detail="Processing failed")



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