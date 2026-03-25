from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from .embedding_utils import generate_Helper
from fastapi import status
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str
    textbook: str
    chapter: str


@router.post("/api/generate")
async def generate_endpoint(request: PromptRequest):
    '''
    This will generate a response using a prompt and provide 
    context to the prompt using a corresponding textbook and
    chapter title

    Inputs:
        prompt: str
        textbook: str
        chapter: str

    '''

    logger.info(f"Generating response for request: ({request.prompt}, {request.textbook}, {request.chapter})")
    prompt = request.prompt
    chapter = request.chapter
    textbook = request.textbook

    try:
        modelResponse = await generate_Helper(prompt, chapter, textbook)

        return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"response": modelResponse}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise
