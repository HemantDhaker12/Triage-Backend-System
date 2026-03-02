from fastapi import APIRouter, Depends, Header
from sqlmodel import Session, select
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.models.state_history import IncidentStateHistory
from app.services.state_machine import validate_transition
from uuid import UUID
from app.core.database import get_session
from app.models.incident import Incident
from app.models.idempotency import IdempotencyKey
from app.utils.hashing import generate_dedup_hash
from app.schemas.incident import IncidentCreate, IncidentResponse

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
        return existing_incident

    # 3️⃣ Create new incident
    incident = Incident(
        title=title,
        description=description,
        source=source,
        dedup_hash=dedup_hash
    )

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