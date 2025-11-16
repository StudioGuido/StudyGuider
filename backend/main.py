from fastapi import FastAPI
from api.generate import router as generate_router
from api.textbooks import router as textbooks_router
from api.chapter import router as chapter_router
from fastapi.middleware.cors import CORSMiddleware
from api.user import router as user_router


from api.generateFlashCard import router as flashcard_router
from api.generateSummary import router as summary_router
app = FastAPI()

# Register endpoints
app.include_router(generate_router)
app.include_router(textbooks_router)
app.include_router(chapter_router)
app.include_router(user_router)

# Change this to match your frontend port (3000)
origins = [
    "http://localhost:3000",
    "http://localhost:5173"
]

# Add CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # <-- important
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(flashcard_router)
app.include_router(summary_router)


# uvicorn main:app --reload
