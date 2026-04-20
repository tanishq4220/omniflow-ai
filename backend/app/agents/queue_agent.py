from app.models.schemas import TelemetryData

class QueueAgent:
    def __init__(self):
        pass

    def calculate_wait_time(self, data: TelemetryData) -> float:
        """Calculate wait time in minutes."""
        if data.service_rate <= 0:
            return 999.0
        return round(data.queue_length / data.service_rate, 2)
