from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi import status

router = APIRouter()


@router.get("/health")
async def getHealth():

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"response": "Healthy"}
    )
    