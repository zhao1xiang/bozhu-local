from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
import uuid

class PatientBase(SQLModel):
    name: str = Field(index=True)
    outpatient_number: Optional[str] = Field(default=None, index=True, description="门诊号")
    medical_card_number: Optional[str] = Field(default=None, description="就诊卡号")
    phone: str = Field(index=True, unique=True, description="手机号")
    diagnosis: Optional[str] = None
    diagnosis_other: Optional[str] = Field(default=None, description="诊断其他说明")
    drug_type: Optional[str] = None
    drug_type_other: Optional[str] = Field(default=None, description="药物其他说明")
    left_vision: Optional[float] = Field(default=None, description="左眼裸眼视力")
    right_vision: Optional[float] = Field(default=None, description="右眼裸眼视力")
    left_vision_corrected: Optional[float] = Field(default=None, description="左眼矫正视力")
    right_vision_corrected: Optional[float] = Field(default=None, description="右眼矫正视力")
    left_eye: bool = False
    right_eye: bool = False
    patient_type: Optional[str] = Field(default=None, description="患者类型") # 初治/经治
    injection_count: Optional[int] = Field(default=None, description="已完成针数（仅经治患者）")
    status: str = Field(default="active", index=True)
    is_deleted: bool = Field(default=False, index=True, description="软删除标记")

class Patient(PatientBase, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    appointments: List["Appointment"] = Relationship(back_populates="patient")
    # schemes relationship removed as schemes are now global templates
    print_records: List["PrintRecord"] = Relationship(back_populates="patient")
