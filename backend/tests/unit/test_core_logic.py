# This test suite validates deterministic outputs for CDI, queue wait time,
# experience scoring, and safety classification to ensure system reliability.
import pytest
from app.agents.crowd_agent import CrowdAgent
from app.agents.queue_agent import QueueAgent
from app.agents.safety_agent import SafetyAgent
from app.core.scoring_engine import ScoringEngine
from app.models.schemas import TelemetryData

def test_calculate_cdi():
    """Verify CDI calculation logic."""
    agent = CrowdAgent()
    data = TelemetryData(people_count=50, max_capacity=100, queue_length=0, service_rate=1.0, emotion_score=0.0)
    assert agent.calculate_cdi(data) == 50.0

def test_calculate_wait_time():
    """Verify queue wait time logic."""
    agent = QueueAgent()
    data = TelemetryData(people_count=0, max_capacity=100, queue_length=20, service_rate=4.0, emotion_score=0.0)
    assert agent.calculate_wait_time(data) == 5.0

def test_experience_score():
    """Verify score calculation falls within 0-100 bounds."""
    engine = ScoringEngine()
    score = engine.calculate_experience_score(wait_time=5.0, cdi=50.0, emotion=100.0)
    assert 0 <= score <= 100
    # Expected: 0.4*(100-5) + 0.3*(100-50) + 0.3*100 = 38 + 15 + 30 = 83.0
    assert score == 83.0

def test_safety_risk_thresholds():
    """Verify safety risk classifications."""
    agent = SafetyAgent()
    assert agent.determine_risk_level(40) == "LOW"
    assert agent.determine_risk_level(60) == "MEDIUM"
    assert agent.determine_risk_level(80) == "HIGH"
    assert agent.determine_risk_level(95) == "CRITICAL"
