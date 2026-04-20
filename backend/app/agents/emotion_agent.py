from app.models.schemas import TelemetryData

class EmotionAgent:
    def __init__(self):
        pass

    def evaluate_emotion(self, data: TelemetryData) -> float:
        """Evaluate raw emotion score, bounded 0-100."""
        return min(max(data.emotion_score, 0.0), 100.0)
