from app.services.ai_client import ai_client


CONFIDENCE_THRESHOLD = 0.65


def classify_with_ai(title: str, description: str):

    try:
        severity, confidence = ai_client.classify(title, description)

        if confidence < CONFIDENCE_THRESHOLD:
            return "MEDIUM", confidence, "fallback"

        return severity, confidence, "ai"

    except Exception:
        return "MEDIUM", 0.0, "fallback"