ALLOWED_TRANSITIONS = {
    "RECEIVED": ["CLASSIFIED", "OVERRIDDEN"],
    "CLASSIFIED": ["ESCALATED", "OVERRIDDEN"],
    "ESCALATED": ["ACKNOWLEDGED", "OVERRIDDEN"],
    "ACKNOWLEDGED": ["RESOLVED", "OVERRIDDEN"],
    "RESOLVED": [],
    "OVERRIDDEN": []
}

def validate_transition(current_state: str, new_state: str):
    allowed = ALLOWED_TRANSITIONS.get(current_state, [])
    if new_state not in allowed:
        raise ValueError(
            f"Illegal transition from {current_state} to {new_state}"
        )