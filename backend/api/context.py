from fastapi import APIRouter
from pydantic import BaseModel
from api.embedding_utils import generate_contextHelper
import logging
import uuid

logger = logging.getLogger(__name__)
router = APIRouter()


class TranscriptRequest(BaseModel):
    transcript: str
    chapter: str
    textbook: str

@router.post("/context")
async def get_context(request: TranscriptRequest):
    request_id = str(uuid.uuid4())
    '''
    This will return 3 chunks of context for next realtimeAPI response. Generates embedding of transcript, 
    similarity search with chunks from specific chapter. Uses cross encoder reranking to return best 3 chunks

    Inputs:
    transcript: str
    chapter: str
    textbook: str
    '''
    logger.info(f"[{request_id}] Searching for best chunks relating to transcript: ({request.transcript}, {request.chapter}, {request.textbook})")
    
    transcript = request.transcript
    chapter = request.chapter
    textbook = request.textbook

    try:
        logger.debug(f"[{request_id}] Calling generate_contextHelper")
        contextResponse = await generate_contextHelper(transcript, chapter, textbook)
        logger.info(f"[{request_id}] Chunks successfully found: {contextResponse}")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={ "response": contextResponse})
    except HTTPException:
        raise
    except Exception as e:
        raise

