from fastapi import FastAPI
from api.generate import router as generate_router
from api.textbooks import router as textbooks_router
from api.chapter import router as chapter_router
from fastapi.middleware.cors import CORSMiddleware
from api.user import router as user_router
from api.user_studymat import router as user_studymat_router

from api.generateFlashCard import router as flashcard_router
from api.generateSummary import router as summary_router

from apscheduler.schedulers.background import BackgroundScheduler
import psycopg2
import os


user_id = '1' # Replace with actual user ID logic????
app = FastAPI()

# Register endpoints
app.include_router(generate_router)
app.include_router(textbooks_router)
app.include_router(chapter_router)
app.include_router(user_router)
app.include_router(user_studymat_router)

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


'''Scheduler to clear seen_card table every 24 hours'''
scheduler = BackgroundScheduler()

# Scheduler setup
scheduler = BackgroundScheduler()

def cleanup():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD")
        )
        cursor = conn.cursor()  
        cursor.execute("DELETE FROM master_flashcard WHERE created_at < NOW() - INTERVAL '7 days';")
        conn.commit()
        cursor.close()
        conn.close()
        print("Old rows deleted")
    except Exception as e:
        print(f"deleting failed: {e}")

@app.on_event("startup")
def start_scheduler():
    scheduler.add_job(cleanup, "interval", seconds=30)
    scheduler.start()
    print("scheduler started")

@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()
    print("scheduler stopped")
