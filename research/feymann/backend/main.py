from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.voice import router as trans

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trans)