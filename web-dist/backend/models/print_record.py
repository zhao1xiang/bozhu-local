from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
import uuid

class PrintRecordBase(SQLModel):
    patient_id: str = Field(foreign_key="patient.id", index=True)
    appointment_id: Optional[str] = Field(default=None, foreign_key="appointment.id")
    print_type: str
    print_data: Optional[str] = None # JSON string

class PrintRecord(PrintRecordBase, table=True):
    __tablename__ = "print_records"
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    print_date: datetime = Field(default_factory=datetime.utcnow)
    
    patient: "Patient" = Relationship(back_populates="print_records")
    appointment: Optional["Appointment"] = Relationship(back_populates="print_records")
