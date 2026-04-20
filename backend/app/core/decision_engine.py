"""
DecisionEngine orchestrates all multi-agent computations.
Now includes overload_factor routing for real-world crowd scale modelling.
"""
from app.models.schemas import TelemetryData, AgentResponse, SystemState
from app.agents.crowd_agent import CrowdAgent
from app.agents.queue_agent import QueueAgent
from app.agents.emotion_agent import EmotionAgent
from app.agents.safety_agent import SafetyAgent
from app.core.prediction_engine import PredictionEngine
from app.core.scoring_engine import ScoringEngine


class DecisionEngine:
    def __init__(self):
        self.crowd = CrowdAgent()
        self.queue = QueueAgent()
        self.emotion = EmotionAgent()
        self.safety = SafetyAgent()
        self.prediction = PredictionEngine()
        self.scoring = ScoringEngine()

    def process_telemetry(self, t: TelemetryData) -> SystemState:
        """Orchestrate all agents and return a full system state."""
        cdi             = self.crowd.calculate_cdi(t)
        overload_factor = self.crowd.calculate_overload_factor(t)
        wait_time       = self.queue.calculate_wait_time(t)
        emo             = self.emotion.evaluate_emotion(t)

        risk  = self.safety.determine_risk_level(overload_factor)
        pred  = self.prediction.predict_congestion_time(cdi, wait_time)
        score = self.scoring.calculate_experience_score(wait_time, cdi, emo)

        # Generate data-driven heatmap (4x4 grid)
        heatmap = [
            round(min(overload_factor * (0.5 + i/20), 5.0), 2)
            for i in range(16)
        ]

        # Generate smart alerts
        alerts = []
        if overload_factor > 1.5:
            alerts.append("🚨 CRITICAL: Extreme crowd overload detected")
        elif overload_factor > 1.0:
            alerts.append("⚠️ HIGH: Capacity exceeded")
        
        if wait_time > 10:
            alerts.append("⏳ Long queue detected")
        
        if emo < 40:
            alerts.append("😟 Low attendee satisfaction")

        # 🚀 Predictive AI (10 min lookahead)
        predicted_people = t.people_count * 1.1 
        predicted_overload = predicted_people / t.max_capacity
        predicted_alert = None
        if predicted_overload > 1.5:
            predicted_alert = "🚨 CRITICAL (10 min): Overload incoming"
        elif predicted_overload > 1:
            predicted_alert = "⚠️ HIGH (10 min): Capacity risk rising"

        resp = AgentResponse(
            cdi=cdi,
            overload_factor=overload_factor,
            wait_time=wait_time,
            safety_risk=risk,
            predicted_congestion=pred,
            heatmap=heatmap,
            alerts=alerts,
            predicted_alert=predicted_alert
        )
        return SystemState(telemetry=t, analysis=resp, experience_score=score)
