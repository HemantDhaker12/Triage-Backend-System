from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class IncidentCreate(BaseModel):
    title: str
    description: str
    source: str


class IncidentResponse(BaseModel):
    id: UUID
    title: str
    description: str
    source: str
    severity: str | None
    confidence_score: float | None
    response_source: str | None
    current_state: str
    dedup_hash: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True