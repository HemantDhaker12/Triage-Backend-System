import hashlib


def generate_dedup_hash(title: str, description: str, source: str) -> str:
    raw = f"{title}|{description}|{source}"
    return hashlib.sha256(raw.encode()).hexdigest()