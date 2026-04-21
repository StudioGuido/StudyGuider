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
import api._creatingEmbeddings as ce

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
    book_id: int
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
    
    conn = None
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        chapter_count = 1

        # Iterate over paths, uploading them to S3 and inserting into DB
        for path in path_arr:
            try:
                s3_key = f"users/{supabase_uid}/textbooks/{textbook_id}/chapters/{chapter_count}"
                # print(f"Uploading {local_file_path} -> {s3_key}")

                # Upload to S3 FIRST
                s3.upload_file(
                    path,
                    BUCKET,
                    s3_key,
                    ExtraArgs={"ContentType": "application/pdf"},
                )

                # Then insert into DB
                await conn.execute(
                    """
                    INSERT INTO chapters (textbook_id, chapter_number, chapter_title)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (textbook_id, chapter_number) DO NOTHING;
                    """,
                    textbook_id,
                    chapter_count,
                    "chapter_title_placeholder",
                )

                uploaded.append(s3_key)
                chapter_count += 1

            except Exception as e:
                failed.append(path)
                print(f"Error uploading {path}: {e}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if conn:
            await conn.close()

    all_ok = len(failed) == 0

    return {
        "message": "All files uploaded successfully" if all_ok else "Some files failed to upload",
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

# Provides frontend with a presigned url for textbook.
@router.post("/api/getPresignedUrl")
async def get_url(user_valid=Depends(verify_jwt)):
    
    supabase_uid = user_valid.get("sub")
    if not supabase_uid:
        raise HTTPException(status_code=401, detail="Missing UID")

    s3_uuid = str(uuid.uuid4())
    key = f"textbooks/{s3_uuid}"

    conn = None
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )
        status="processing"
        row = await conn.fetchrow(
            """
            INSERT INTO textbooks (user_uid, title, author, description, image_path, status)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id;
            """,
            supabase_uid,
            "title_placeholder",
            "author_placeholder",
            "desc_placeholder",
            "image_path_placeholder",
            status,
        )

        textbook_id = row["id"]
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

# Provides frontend with a presigned url for textbook chapter.
@router.get("/api/textbooks/{textbook_id}/chapters/{chapter_id}/pdf")
async def get_chapter_pdf_url(
    textbook_id: int,
    chapter_id: int,
    user_valid=Depends(verify_jwt),
):
    supabase_uid = user_valid.get("sub")
    if not supabase_uid:
        raise HTTPException(status_code=401, detail="Missing UID")

    conn = None
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

        # Verify ownership + existence
        row = await conn.fetchrow(
            """
            SELECT c.chapter_number
            FROM chapters c
            JOIN textbooks t ON c.textbook_id = t.id
            WHERE c.chapter_number = $1
              AND t.id = $2
              AND t.user_uid = $3;
            """,
            chapter_id,
            textbook_id,
            supabase_uid,
        )

        if not row:
            raise HTTPException(status_code=404, detail="Chapter not found")

    except HTTPException:
        raise
    except Exception as e:
        # log e internally
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        if conn:
            await conn.close()

    # ✅ Construct S3 key (now safe)
    key = f"users/{supabase_uid}/textbooks/{textbook_id}/chapters/{chapter_id}"

    try:
        url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": BUCKET,
                "Key": key,
            },
            ExpiresIn=3600,  # 1 hour
        )
    except Exception as e:
        # log e internally
        raise HTTPException(status_code=500, detail="Failed to generate URL")

    return {
        "presigned_url": url,
        "file_key": key,
    }


@router.post("/process-pdf")
async def trigger_pdf_processing(request: ProcessRequest, user_valid=Depends(verify_jwt)):
    print("\n\n1\n\n")
    supabase_uid = user_valid.get("sub")
    if not supabase_uid:
        raise HTTPException(status_code=401, detail="Missing UID")

    try:
        print(f"[{request.book_id}] Processing started...")

        # downloads file from s3 (uploaded to via frontend)
        download_file(request.file_key, "downloaded_textbook.pdf")
        
        # Generates list of local downloaded chapter paths
        listOfChapters, book_title = rc.extract_chapters_from_pdf_Updated_Better_Version("downloaded_textbook.pdf", supabase_uid)
        
        # TODO: Call creating embeddings function here
        # Debugging Embeddings
        # for p in listOfChapters:
        #     print(repr(p), "exists:", os.path.exists(p) if isinstance(p, str) else "not-a-str", flush=True)

        # print("\n\n100000\n\n")
        ce.createEmbeddings(listOfChapters)
        # await ce.fillTables(listOfChapters, request.book_id)
        # print("\n\n200000\n\n")
        """
        1. Run the app with s3 upload once to get the seperate files
        2. Write your helper function that will create embeddings
        2.5 Add those embeddings to the database
        3. Test that you are doing this correctly
        4. Then you can integrate it into the main code.
        5. Merge your code with Pierce's code
        
        """
        # creates keys from filepaths and uploads chunks to s3
        # await upload(supabase_uid, listOfChapters)
        

        print("\n\n Uploading textbook: ", textbook_title, flush=True)
        # creates keys from filepaths and uploads chunks to s3
        await upload(supabase_uid, listOfChapters, request.book_id)
        print("\n\n Finished uploading textbook\n\n")


        print(f"[{request.book_id}] Processing complete.\n\n")
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
                SET status = 'complete',
                  textbook_title = $1
                WHERE textbook_id = $2
                """,
                request.book_id,  # only one argument to match only $1
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
async def get_job_status(textbook_id: int):
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
            FROM textbooks
            WHERE id = $1
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