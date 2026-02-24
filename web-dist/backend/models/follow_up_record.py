from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime

class FollowUpRecordBase(SQLModel):
    appointment_id: str = Field(foreign_key="appointment.id")
    patient_id: str = Field(foreign_key="patient.id")
    status: str # e.g., "confirmed", "no_answer", "rescheduled"
    notes: Optional[str] = None
    follow_up_date: datetime = Field(default_factory=datetime.now)

class FollowUpRecord(FollowUpRecordBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)

class FollowUpRecordCreate(FollowUpRecordBase):
    pass
