from sqlmodel import SQLModel, Field
from datetime import datetime


class IdempotencyKey(SQLModel, table=True):
    key: str = Field(primary_key=True)
    incident_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)