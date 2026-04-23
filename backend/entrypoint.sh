#!/bin/bash

echo "⏳ Initializing database..."

# setting up database
python createTables.py
python moveToDb.py


# python warmModel.py

PYTHONPATH=. pytest testAPI/test_flashcard_integration.py -v
 

# starting up the server
echo "🚀 Starting FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
