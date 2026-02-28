from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from .embedding_utils import generate_Helper
from fastapi import status
from fastapi.responses import JSONResponse


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
    print("in\n\n")
    prompt = request.prompt
    chapter = request.chapter
    textbook = request.textbook

    print("in\n\n")

    try:
        modelResponse, context = await generate_Helper(prompt, chapter, textbook) # added context

        return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"response": modelResponse, "context": context} # return content with context included
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise
