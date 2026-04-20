# This test suite validates deterministic outputs for CDI, queue wait time,
# experience scoring, and safety classification to ensure system reliability.
from app.agents.crowd_agent import CrowdAgent
from app.agents.queue_agent import QueueAgent
from app.agents.safety_agent import SafetyAgent
from app.agents.emotion_agent import EmotionAgent
from app.models.schemas import TelemetryData
import pytest

def test_crowd_agent():
    agent = CrowdAgent()
    data = TelemetryData(people_count=5000, max_capacity=10000, queue_length=0, service_rate=1.0, emotion_score=0.0)
    assert agent.calculate_cdi(data) == 50.0

def test_crowd_agent_zero_cap():
    agent = CrowdAgent()
    data = TelemetryData(people_count=100, max_capacity=0, queue_length=0, service_rate=1.0, emotion_score=0.0)
    assert agent.calculate_cdi(data) == 0.0

def test_queue_agent():
    agent = QueueAgent()
    data = TelemetryData(people_count=0, max_capacity=1, queue_length=100, service_rate=5.0, emotion_score=0.0)
    assert agent.calculate_wait_time(data) == 20.0

def test_queue_agent_zero_rate():
    agent = QueueAgent()
    data = TelemetryData(people_count=0, max_capacity=1, queue_length=100, service_rate=0.0, emotion_score=0.0)
    assert agent.calculate_wait_time(data) == 999.0

def test_safety_agent():
    agent = SafetyAgent()
    assert agent.determine_risk_level(40) == "LOW"
    assert agent.determine_risk_level(60) == "MEDIUM"
    assert agent.determine_risk_level(80) == "HIGH"
    assert agent.determine_risk_level(95) == "CRITICAL"

def test_emotion_agent():
    agent = EmotionAgent()
    data = TelemetryData(people_count=0, max_capacity=1, queue_length=0, service_rate=1.0, emotion_score=150.0)
    assert agent.evaluate_emotion(data) == 100.0
