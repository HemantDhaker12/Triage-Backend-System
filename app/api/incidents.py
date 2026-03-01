from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.models.incident import Incident

router = APIRouter()


@router.post("/incidents")
def create_incident(payload: dict, session: Session = Depends(get_session)):
    incident = Incident(
        title=payload.get("title", "untitled"),
        description=payload.get("description", ""),
        source=payload.get("source", "unknown"),
    )

    session.add(incident)
    session.commit()
    session.refresh(incident)

    return incident


@router.get("/incidents")
def list_incidents(session: Session = Depends(get_session)):
    return session.query(Incident).all()