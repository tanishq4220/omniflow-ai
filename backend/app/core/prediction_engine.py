class PredictionEngine:
    def __init__(self):
        pass

    def predict_congestion_time(self, cdi: float, wait_time: float) -> int:
        """Predict minutes until critical congestion. O(1) logic for single metric processing."""
        if cdi >= 90:
            return 0
        minutes_left = (100 - cdi) * 0.5 - (wait_time * 0.1)
        return max(0, int(round(minutes_left)))
