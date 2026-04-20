# This test suite validates deterministic outputs for CDI, queue wait time,
# experience scoring, and safety classification to ensure system reliability.
from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app, raise_server_exceptions=False)

def test_analyze_endpoint_contract():
    """Verify integration contract for /analyze endpoint."""
    # Obtain auth token
    resp = client.post("/api/token", json={"username": "admin", "password": "password123"})
    assert resp.status_code == 200, f"Auth failed"
    token = resp.json()["access_token"]

    payload = {
        "people_count": 80,
        "max_capacity": 100,
        "queue_length": 20,
        "service_rate": 5,
        "emotion_score": 100
    }
    
    response = client.post("/api/analyze", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, f"Failed: {response.text}"
    
    data = response.json()
    assert "analysis" in data
    analysis = data["analysis"]
    
    assert analysis["cdi"] == 80.0
    assert analysis["wait_time"] == 4.0
    assert "safety_risk" in analysis
    assert data["experience_score"] is not None
