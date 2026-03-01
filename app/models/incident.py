from sqlmodel import SQLModel, Field
from uuid import uuid4, UUID
from datetime import datetime


class Incident(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    title: str
    description: str
    source: str

    severity: str | None = None
    confidence_score: float | None = None
    response_source: str | None = None

    current_state: str = "RECEIVED"

    dedup_hash: str | None = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)