import pytest
from fastapi.testclient import TestClient

def test_connect_openAI(client):
    """
    Test connecting to the openAI realtime API using TestClient
    """
    response = client.get("/api/session")
    data = response.json()
    assert response.status_code == 200
    assert data["client_secret"]["value"] is not None
