class SafetyAgent:
    def __init__(self):
        pass

    def determine_risk_level(self, cdi: float) -> str:
        """Determine safety risk based on CDI."""
        if cdi < 50:
            return "LOW"
        elif cdi <= 75:
            return "MEDIUM"
        elif cdi <= 90:
            return "HIGH"
        return "CRITICAL"
