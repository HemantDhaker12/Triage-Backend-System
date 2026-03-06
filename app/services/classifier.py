def classify_incident(title: str, description: str):
    text = f"{title} {description}".lower()

    if "database" in text:
        return "CRITICAL", 0.95, "rule"

    if "server" in text:
        return "HIGH", 0.8, "rule"

    return "MEDIUM", 0.5, "fallback"