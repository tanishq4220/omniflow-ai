from app.models.schemas import TelemetryData


class CrowdAgent:
    def calculate_cdi(self, data: TelemetryData) -> float:
        """Calculate normalized Crowd Density Index (0–100 cap)."""
        if data.max_capacity == 0:
            return 0.0
        raw = (data.people_count / data.max_capacity) * 100
        return round(min(raw, 100.0), 2)

    def calculate_overload_factor(self, data: TelemetryData) -> float:
        """
        Real-world overload factor: ratio of people to capacity.
        Values >1.0 indicate overcrowding (e.g. 1.5x = 50% over capacity).
        """
        if data.max_capacity == 0:
            return 0.0
        return round(data.people_count / data.max_capacity, 3)
