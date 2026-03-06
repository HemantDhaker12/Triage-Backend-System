from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class AuditLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    incident_id: Optional[UUID] = Field(default=None)

    stage: str
    payload: str

    timestamp: datetime = Field(default_factory=datetime.utcnow)