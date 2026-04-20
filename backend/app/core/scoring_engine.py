class ScoringEngine:
    def __init__(self):
        pass

    def calculate_experience_score(self, wait_time: float, cdi: float, emotion: float) -> float:
        """Calculate score based on deterministic formula."""
        score = 0.4 * (100 - wait_time) + 0.3 * (100 - cdi) + 0.3 * emotion
        return min(max(round(score, 2), 0.0), 100.0)
