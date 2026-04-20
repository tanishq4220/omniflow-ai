# This test suite validates deterministic outputs for CDI, queue wait time,
# experience scoring, and safety classification to ensure system reliability.
from app.core.prediction_engine import PredictionEngine
from app.core.scoring_engine import ScoringEngine
from app.core.decision_engine import DecisionEngine
from app.models.schemas import TelemetryData
import pytest

def test_prediction_engine():
    engine = PredictionEngine()
    assert engine.predict_congestion_time(90, 10) == 0
    assert engine.predict_congestion_time(50, 100) == 15

def test_scoring_engine():
    engine = ScoringEngine()
    score = engine.calculate_experience_score(20, 50, 80)
    assert score == 71.0

def test_decision_engine():
    engine = DecisionEngine()
    data = TelemetryData(people_count=7500, max_capacity=10000, queue_length=50, service_rate=5.0, emotion_score=60.0)
    state = engine.process_telemetry(data)
    assert state.analysis.cdi == 75.0
    assert state.analysis.wait_time == 10.0
    assert state.analysis.safety_risk == "MEDIUM"
