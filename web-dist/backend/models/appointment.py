from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import date, datetime, timezone
import uuid

class AppointmentBase(SQLModel):
    patient_id: str = Field(foreign_key="patient.id", index=True)
    appointment_date: Optional[date] = Field(default=None, index=True)
    time_slot: Optional[str] = None
    status: str = Field(default="scheduled", index=True)
    notes: Optional[str] = None
    is_deleted: bool = Field(default=False, index=True, description="软删除标记")
    
    # New fields
    injection_number: Optional[str] = None # 注药号
    injection_count: Optional[int] = None # 注药次数
    eye: Optional[str] = None # 眼别 (左眼/右眼)
    drug_name: Optional[str] = None # 药品名称
    drug_name_other: Optional[str] = Field(default=None, description="药品其他说明")
    cost_type: Optional[str] = None # 费别 (自费/医保)
    doctor: Optional[str] = None # 注药医生
    attending_doctor: Optional[str] = Field(default=None, description="管床医生")
    virus_report: Optional[str] = Field(default=None, description="病毒报告")
    blood_sugar: Optional[str] = Field(default=None, description="血糖")
    blood_pressure: Optional[str] = Field(default=None, description="血压")
    left_eye_pressure: Optional[str] = Field(default=None, description="左眼压")
    right_eye_pressure: Optional[str] = Field(default=None, description="右眼压")
    eye_wash_result: Optional[str] = Field(default=None, description="冲眼结果")
    follow_up_date: Optional[date] = None # 复诊时间
    next_follow_up_date: Optional[date] = None # 下次复诊时间
    diagnosis: Optional[str] = None # 诊断
    pre_op_vision_left: Optional[float] = None # 左眼术前视力
    pre_op_vision_right: Optional[float] = None # 右眼术前视力
    treatment_phase: Optional[str] = Field(default=None, description="治疗周期") # 强化期/巩固期

class Appointment(AppointmentBase, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    patient: "Patient" = Relationship(back_populates="appointments")
    print_records: List["PrintRecord"] = Relationship(back_populates="appointment")
