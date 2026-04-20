# This test suite validates JWT authentication enforcement, input validation,
# and end-to-end API contract correctness for the OmniFlow AI security layer.
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)

VALID_PAYLOAD = {
    "people_count": 80,
    "max_capacity": 100,
    "queue_length": 20,
    "service_rate": 5.0,
    "emotion_score": 70.0,
}


# ---------- Auth helpers ----------
def get_token() -> str:
    """Obtain a valid JWT by logging in with default credentials."""
    resp = client.post("/api/token", json={"username": "admin", "password": "password123"})
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------- Security: Unauthorized access ----------
def test_analyze_no_token_returns_401():
    """POST /api/analyze without token must return 401 Unauthorized."""
    resp = client.post("/api/analyze", json=VALID_PAYLOAD)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"


def test_analyze_invalid_token_returns_401():
    """POST /api/analyze with a fake token must return 401 Unauthorized."""
    resp = client.post(
        "/api/analyze",
        json=VALID_PAYLOAD,
        headers={"Authorization": "Bearer totally.fake.token"},
    )
    assert resp.status_code == 401


def test_analyze_malformed_header_returns_401():
    """POST /api/analyze with malformed Authorization header returns 401."""
    resp = client.post(
        "/api/analyze",
        json=VALID_PAYLOAD,
        headers={"Authorization": "Basic abc123"},
    )
    assert resp.status_code == 401


# ---------- Input validation ----------
def test_analyze_negative_people_count_returns_422():
    """Negative people_count violates ge=0 constraint → 422 Unprocessable."""
    token = get_token()
    bad_payload = {**VALID_PAYLOAD, "people_count": -1}
    resp = client.post("/api/analyze", json=bad_payload, headers=auth_headers(token))
    assert resp.status_code == 422


def test_analyze_zero_service_rate_returns_422():
    """service_rate=0 violates gt=0 constraint → 422 Unprocessable."""
    token = get_token()
    bad_payload = {**VALID_PAYLOAD, "service_rate": 0}
    resp = client.post("/api/analyze", json=bad_payload, headers=auth_headers(token))
    assert resp.status_code == 422


def test_analyze_emotion_score_out_of_range_returns_422():
    """emotion_score=150 violates le=100 constraint → 422 Unprocessable."""
    token = get_token()
    bad_payload = {**VALID_PAYLOAD, "emotion_score": 150}
    resp = client.post("/api/analyze", json=bad_payload, headers=auth_headers(token))
    assert resp.status_code == 422


def test_analyze_missing_field_returns_422():
    """Missing required field returns 422 Unprocessable Entity."""
    token = get_token()
    resp = client.post("/api/analyze", json={"people_count": 50}, headers=auth_headers(token))
    assert resp.status_code == 422


# ---------- Valid request ----------
def test_analyze_valid_authenticated_request_returns_200():
    """Valid payload + valid token → 200 with correct CDI and wait_time."""
    token = get_token()
    resp = client.post("/api/analyze", json=VALID_PAYLOAD, headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert "analysis" in data
    assert data["analysis"]["cdi"] == pytest.approx(80.0)
    assert data["analysis"]["wait_time"] == pytest.approx(4.0)
    assert data["analysis"]["safety_risk"] in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    assert 0 <= data["experience_score"] <= 100


# ---------- Health endpoint ----------
def test_health_returns_ok_without_auth():
    """GET /api/health is publicly accessible and returns status OK."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "OK"
    assert "services" in body
