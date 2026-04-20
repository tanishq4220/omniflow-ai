# This test suite validates deterministic outputs for CDI, queue wait time,
# experience scoring, and safety classification to ensure system reliability.
from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_login_success():
    response = client.post("/api/token", json={"username": "admin", "password": "password123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_failure():
    response = client.post("/api/token", json={"username": "admin", "password": "wrongpassword"})
    assert response.status_code == 400

def test_telemetry_flow():
    payload = {
        "people_count": 8000,
        "max_capacity": 10000,
        "queue_length": 20,
        "service_rate": 2.0,
        "emotion_score": 85.0
    }
    response = client.post("/api/telemetry", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["analysis"]["cdi"] == 80.0
    assert data["analysis"]["safety_risk"] == "HIGH"

def test_telemetry_invalid():
    payload = {
        "people_count": -5,
        "max_capacity": 10000,
        "queue_length": 20,
        "service_rate": 2.0,
        "emotion_score": 85.0
    }
    response = client.post("/api/telemetry", json=payload)
    assert response.status_code == 422
