class DecisionAuthority:
    def __init__(self, pc_threshold=0.0001):
        self.threshold = pc_threshold

    def evaluate(self, pc, fuel_impact):
        """
        Decides if a maneuver should be executed.
        """
        if pc >= self.threshold:
            return {
                "decision": "EXECUTE MANEUVER",
                "reason": f"Probability {pc} exceeds threshold {self.threshold}",
                "priority": "HIGH" if pc > 0.01 else "MEDIUM"
            }
        else:
            return {
                "decision": "MONITOR ONLY",
                "reason": f"Probability {pc} is below threshold",
                "priority": "LOW"
            }
