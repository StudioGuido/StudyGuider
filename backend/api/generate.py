from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from .embedding_utils import generate_Helper
from fastapi import status
from fastapi.responses import JSONResponse
import logging
import uuid


logger = logging.getLogger(__name__)
router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str
    textbook: str
    chapter: str


@router.post("/api/generate")
async def generate_endpoint(request: PromptRequest):

    request_id = str(uuid.uuid4())

    '''
    This will generate a response using a prompt and provide 
    context to the prompt using a corresponding textbook and
    chapter title

    Inputs:
        prompt: str
        textbook: str
        chapter: str

    '''

    logger.info(f"[{request_id}] Generating response for request: ({request.prompt}, {request.textbook}, {request.chapter})")
    prompt = request.prompt
    chapter = request.chapter
    textbook = request.textbook

    try:
        logger.debug(f"[{request_id}] Calling generate_Helper")
        modelResponse = await generate_Helper(prompt, chapter, textbook)
        logger.info(f"[{request_id}] Generation Successful with response length: {len(modelResponse)}")

        return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"response": modelResponse})
    
    except HTTPException:
        raise
    except Exception as e:
        raise
