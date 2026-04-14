import pytest
from fastapi.testclient import TestClient



def test_get_all_textbooks(client):
    """
    Test retrieving all the textbooks using TestClient
    """
    response = client.get("/api/getTextbooks")
    assert response.status_code == 200
    
    res = response.json()
    assert "response" in res, "Key 'response' missing in JSON"
