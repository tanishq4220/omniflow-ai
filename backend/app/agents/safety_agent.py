class SafetyAgent:
    def determine_risk_level(self, overload_factor: float) -> str:
        """
        Determine safety risk based on real-world overload factor.
        <0.8  → LOW
        0.8–1.0 → MEDIUM
        1.0–1.5 → HIGH
        >1.5  → CRITICAL
        """
        if overload_factor < 0.8:
            return "LOW"
        elif overload_factor <= 1.0:
            return "MEDIUM"
        elif overload_factor <= 1.5:
            return "HIGH"
        return "CRITICAL"
