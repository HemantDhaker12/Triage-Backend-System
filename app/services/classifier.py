from app.services.ai_classifier import classify_with_ai


def classify_incident(title: str, description: str):

    text = f"{title} {description}".lower()

    # --- Rule Engine ---
    if "database" in text:
        return "CRITICAL", 0.95, "rule"

    if "server" in text:
        return "HIGH", 0.9, "rule"

    # --- AI Classification ---
    return classify_with_ai(title, description)