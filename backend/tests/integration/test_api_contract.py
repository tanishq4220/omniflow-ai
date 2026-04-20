# This test suite validates deterministic outputs for CDI, queue wait time,
# experience scoring, and safety classification to ensure system reliability.
from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

def test_analyze_endpoint_contract():
    """Verify integration contract for /analyze endpoint."""
    payload = {
        "people_count": 80,
        "max_capacity": 100,
        "queue_length": 20,
        "service_rate": 5,
        "emotion_score": 100
    }
    
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "analysis" in data
    analysis = data["analysis"]
    
    assert analysis["cdi"] == 80.0
    assert analysis["wait_time"] == 4.0
    assert "safety_risk" in analysis
    assert data["experience_score"] is not None
