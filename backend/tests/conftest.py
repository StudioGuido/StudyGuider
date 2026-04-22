import pytest
import asyncpg
import os
import pytest_asyncio
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    # setup TestClient
    return TestClient(app)

@pytest_asyncio.fixture
async def db():
    conn = await asyncpg.connect(
        host=os.getenv("DATABASE_HOST"),
        database=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD")
    )

    #add ben test user to table for test
    await conn.execute(
        "INSERT INTO users (supabase_uid) VALUES ($1) ON CONFLICT DO NOTHING",
        'e6a6c7c5-4360-4722-8c0a-75ff8bff5b1f'
    )
    yield conn
    await conn.close()