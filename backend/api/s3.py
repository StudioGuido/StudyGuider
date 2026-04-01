import boto3
import os
import uuid
from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from api.auth import verify_jwt
from pydantic import BaseModel

router = APIRouter()

# specific bucket
BUCKET = "sg-textbooks"


# create S3 client
# s3 = boto3.client(
#     "s3",
#     aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
#     aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
#     aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
#     region_name=os.getenv("AWS_DEFAULT_REGION")
# )

s3 = boto3.client("s3")

class ProcessRequest(BaseModel):
    book_id: str
    file_key: str

def upload_file(local_path: str):
    filename = os.path.basename(local_path)
    file_id = str(uuid.uuid4())
    key = f"textbooks/chapter1/{file_id}-{filename}"

    # upload file to S3
    s3.upload_file(
        local_path,
        BUCKET,
        key,
        ExtraArgs={"ContentType": "application/pdf"}
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
    
    # Step A: Download file from S3 using boto3
    # Step B: Open PDF with PyMuPDF and find chapters
    # Step C: Split PDF into new files
    # Step D: Upload new files to S3 (processed/book_id/...)
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
    
    file_id = str(uuid.uuid4())
    key = f"textbooks/{file_id}"
    
    url = s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": BUCKET,
            "Key": key,
            "ContentType": "application/pdf"
        },
        ExpiresIn=300
    )
    return {"presigned_url": url}

@router.post("/process-pdf")
async def trigger_pdf_processing(request: ProcessRequest, background_tasks: BackgroundTasks):
    
    # Add the heavy-lifting function to FastAPI's background queue.
    # We pass the function name, followed by its arguments.
    background_tasks.add_task(
        split_pdf_worker, 
        book_id=request.book_id, 
        file_key=request.file_key
    )
    
    # Update your database here to mark this book_id as "Processing"
    
    # Instantly return a 202 status to the frontend.
    # We do NOT wait for the split_pdf_worker to finish!
    return {
        "message": "Processing started in the background.",
        "book_id": request.book_id,
        "status": "processing"
    }

# Uploads Chunked Textbook.
@router.post("/api/uploadTextbookChapters")
async def get(file_id: str, user_valid=Depends(verify_jwt)):
    
    supabase_uid = user_valid.get("sub")
    if not supabase_uid:
        raise HTTPException(status_code=401, detail="Missing UID")