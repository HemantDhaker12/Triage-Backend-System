class Metrics:
    def __init__(self):
        self.total_incidents = 0
        self.rule_classifications = 0
        self.fallback_classifications = 0
        self.auto_escalations = 0
        self.ai_classifications = 0
        self.ai_failures = 0

    def as_dict(self):
        return {
            "total_incidents": self.total_incidents,
            "rule_classifications": self.rule_classifications,
            "fallback_classifications": self.fallback_classifications,
            "auto_escalations": self.auto_escalations,
            "ai_classifications": self.ai_classifications,
            "ai_failures": self.ai_failures,
        }


metrics = Metrics()