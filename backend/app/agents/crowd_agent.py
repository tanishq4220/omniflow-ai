from app.models.schemas import TelemetryData

class CrowdAgent:
    def __init__(self):
        pass

    def calculate_cdi(self, data: TelemetryData) -> float:
        """Calculate Crowd Density Index."""
        if data.max_capacity == 0:
            return 0.0
        return round((data.people_count / data.max_capacity) * 100, 2)
