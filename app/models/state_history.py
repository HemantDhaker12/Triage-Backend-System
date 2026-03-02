from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID


class IncidentStateHistory(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    incident_id: UUID = Field(foreign_key="incident.id")

    from_state: str
    to_state: str
    reason: str

    timestamp: datetime = Field(default_factory=datetime.utcnow)