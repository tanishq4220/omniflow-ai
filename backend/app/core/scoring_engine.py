class ScoringEngine:
    def calculate_experience_score(
        self, wait_time: float, cdi: float, emotion: float
    ) -> float:
        """
        Deterministic experience score formula (0–100).
        score = 0.4*(100-wait_time) + 0.3*(100-CDI) + 0.3*emotion_score
        CDI is always 0–100 (normalized), ensuring no negative components.
        """
        score = (
            0.4 * (100 - min(wait_time, 100))
            + 0.3 * (100 - cdi)          # CDI already capped 0–100
            + 0.3 * emotion
        )
        return min(max(round(score, 2), 0.0), 100.0)
