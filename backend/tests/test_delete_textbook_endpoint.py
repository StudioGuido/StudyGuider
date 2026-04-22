import pytest
from fastapi.testclient import TestClient
from main import app
from api.auth import verify_jwt
import json

def override_verify_jwt():
    return {"sub": "e6a6c7c5-4360-4722-8c0a-75ff8bff5b1f"} #ben uid

app.dependency_overrides[verify_jwt] = override_verify_jwt

@pytest.mark.asyncio
async def test_delete_textbook_endpoint(client, db):
    """
    Test deleting textbook associated with certain user
    """
    #first add textbook
    row = await db.fetchrow(
        "INSERT INTO textbooks (title, user_uid, author, description, image_path, status) VALUES ($1, $2, $3, $4, $5, $6) RETURNING id",
        'Test Book', 'e6a6c7c5-4360-4722-8c0a-75ff8bff5b1f', 'Test Author', 'Test description', '/test.jpg', 'active'
    )
    textbook_id = row['id']

    #now delete via endpoint
    
    response = client.delete(f"/api/delete_textbook?textbook_id={str(textbook_id)}")

    assert response.status_code == 200
    res = response.json()
    assert "message" in res