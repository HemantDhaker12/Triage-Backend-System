from fastapi import APIRouter, Depends, Header
from sqlmodel import Session, select
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.models.state_history import IncidentStateHistory
from app.services.state_machine import validate_transition
from app.services.classifier import classify_incident
from app.models.state_history import IncidentStateHistory
from app.services.state_machine import validate_transition
from uuid import UUID
from app.core.database import get_session
from app.models.incident import Incident
from app.models.idempotency import IdempotencyKey
from app.utils.hashing import generate_dedup_hash
from app.schemas.incident import IncidentCreate, IncidentResponse
from app.services.audit import log_audit
from app.core.metrics import metrics
router = APIRouter()


@router.post("/incidents", response_model=IncidentResponse)
def create_incident(
    payload: IncidentCreate,
    session: Session = Depends(get_session),
    x_idempotency_key: str | None = Header(default=None)
):
    title = payload.title
    description = payload.description
    source = payload.source
    log_audit(session, None, "intake_received", payload.dict())
    
    # 1️⃣ Idempotency Check
    if x_idempotency_key:
        existing_key = session.get(IdempotencyKey, x_idempotency_key)
        if existing_key:
            incident = session.get(Incident, UUID(existing_key.incident_id))
            return incident

    # 2️⃣ Dedup Check (10 min window)
    dedup_hash = generate_dedup_hash(title, description, source)
    window_start = datetime.utcnow() - timedelta(minutes=10)

    statement = select(Incident).where(
        Incident.dedup_hash == dedup_hash,
        Incident.created_at >= window_start
    )
    existing_incident = session.exec(statement).first()

    if existing_incident:
        log_audit(session, existing_incident.id, "dedup_hit", {
        "hash": dedup_hash
    })
        session.commit()
        return existing_incident
    # 3️⃣ Create new incident
    incident = Incident(
        title=title,
        description=description,
        source=source,
        dedup_hash=dedup_hash,
        raw_payload=payload.dict()
    )

    session.add(incident)
    session.commit()
    session.refresh(incident)
    metrics.total_incidents += 1
        # --- Classification ---
    severity, confidence, source_type = classify_incident(
        incident.title, incident.description
    )
    log_audit(session, incident.id, "classification_result", {
        "severity": severity,
        "confidence": confidence,
        "source": source_type
    })
    if source_type == "rule":
        metrics.rule_classifications += 1
    elif source_type == "ai":
        metrics.ai_classifications += 1
    else:
        metrics.fallback_classifications += 1
    incident.severity = severity
    incident.confidence_score = confidence
    incident.response_source = source_type

    # --- Transition to CLASSIFIED ---
    try:
        validate_transition(incident.current_state, "CLASSIFIED")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    history = IncidentStateHistory(
        incident_id=incident.id,
        from_state=incident.current_state,
        to_state="CLASSIFIED",
        reason="automatic classification"
    )

    session.add(history)

    incident.current_state = "CLASSIFIED"
        # --- Auto Escalation ---
    if incident.severity in ["HIGH", "CRITICAL"]:
        try:
            validate_transition(incident.current_state, "ESCALATED")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        escalation_history = IncidentStateHistory(
            incident_id=incident.id,
            from_state=incident.current_state,
            to_state="ESCALATED",
            reason="automatic escalation due to severity"
        )
        log_audit(session, incident.id, "auto_escalation", {
        "severity": incident.severity
        })
        session.add(escalation_history)

        incident.current_state = "ESCALATED"
        session.add(incident)
        session.commit()
        session.refresh(incident)
        metrics.auto_escalations += 1
    session.add(incident)
    session.commit()
    session.refresh(incident)

    # 4️⃣ Store idempotency key
    if x_idempotency_key:
        idempotency_record = IdempotencyKey(
            key=x_idempotency_key,
            incident_id=str(incident.id)
        )
        session.add(idempotency_record)
        session.commit()

    return incident


@router.get("/incidents", response_model=list[IncidentResponse])
def list_incidents(session: Session = Depends(get_session)):
    statement = select(Incident)
    incidents = session.exec(statement).all()
    return incidents
@router.patch("/incidents/{incident_id}/state", response_model=IncidentResponse)
def update_state(
    incident_id: UUID,
    new_state: str,
    reason: str,
    session: Session = Depends(get_session)
):
    incident = session.get(Incident, incident_id)

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    try:
        validate_transition(incident.current_state, new_state)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Log history
    history = IncidentStateHistory(
        incident_id=incident.id,
        from_state=incident.current_state,
        to_state=new_state,
        reason=reason
    )

    session.add(history)

    # Update state
    incident.current_state = new_state
    incident.updated_at = datetime.utcnow()

    session.add(incident)
    session.commit()
    session.refresh(incident)

    return incident
@router.get("/metrics")
def get_metrics():
    return metrics.as_dict()

@router.post("/incidents/{incident_id}/replay", response_model=IncidentResponse)
def replay_incident(
    incident_id: UUID,
    session: Session = Depends(get_session)
):

    incident = session.get(Incident, incident_id)

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if not incident.raw_payload:
        raise HTTPException(status_code=400, detail="No raw payload available")

    payload = incident.raw_payload

    # Re-run ingestion pipeline
    new_incident = Incident(
        title=payload["title"],
        description=payload["description"],
        source=payload["source"],
        raw_payload=payload
    )

    session.add(new_incident)
    session.commit()
    session.refresh(new_incident)

    return new_incident

@router.post("/incidents/{incident_id}/override", response_model=IncidentResponse)
def override_incident(
    incident_id: UUID,
    severity: str,
    reason: str,
    session: Session = Depends(get_session)
):

    incident = session.get(Incident, incident_id)

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Change severity
    incident.severity = severity

    # Validate state change
    try:
        validate_transition(incident.current_state, "OVERRIDDEN")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    history = IncidentStateHistory(
        incident_id=incident.id,
        from_state=incident.current_state,
        to_state="OVERRIDDEN",
        reason=reason
    )

    session.add(history)

    incident.current_state = "OVERRIDDEN"

    session.add(incident)
    session.commit()
    session.refresh(incident)

    return incident