import pytest
from fastapi.testclient import TestClient

def test_get_context(client):
    """
    Test retrieving best chunks using TestClient given transcript, chapter, textbook
    """
    response = client.post("/api/context", json={
        "transcript": "program's in python",
        "chapter": "The Way of the Program",
        "textbook": "thinkpython2"
    })

    assert response.status_code == 200

    res = response.json()
    assert "response" in res, "Key 'response' missing in JSON"