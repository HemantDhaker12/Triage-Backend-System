import random


class AIClient:

    def classify(self, title: str, description: str):
        text = f"{title} {description}".lower()

        # Simulate AI reasoning
        if "latency" in text:
            return "HIGH", 0.85

        if "timeout" in text:
            return "CRITICAL", 0.9

        if "slow" in text:
            return "MEDIUM", 0.7

        # Simulate uncertain AI response
        return "LOW", random.uniform(0.3, 0.6)


ai_client = AIClient()