import json
from sqlmodel import Session
from app.models.audit import AuditLog


def log_audit(session: Session, incident_id, stage: str, payload: dict):
    record = AuditLog(
        incident_id=incident_id,
        stage=stage,
        payload=json.dumps(payload)
    )
    session.add(record)