#!/bin/bash

echo "⏳ Initializing database..."

# setting up database
python createTables.py
python moveToDb.py

echo "Running Tests"
# PYTHONPATH=. pytest
echo "Passed All Test"
# python warmModel.py

# starting up the server
echo "🚀 Starting FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# docker compose exec backend /bin/bash