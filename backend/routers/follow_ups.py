from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from database import engine
from models import Appointment, FollowUpRecord, FollowUpRecordCreate, SystemSetting, Patient
from models.user import User
from security import get_current_user
from typing import List, Optional
from datetime import date, timedelta

router = APIRouter(prefix="/follow-ups", tags=["follow-ups"])

def get_session():
    with Session(engine) as session:
        yield session

def apply_doctor_filter(query, current_user: User):
    """为医生账号应用权限过滤"""
    if current_user.role == 'doctor':
        # 医生只能看自己的复诊提醒
        query = query.where(Appointment.doctor == current_user.doctor)
    return query

@router.get("/reminders")
def get_reminders(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # 1. Get advance days setting
    setting = session.exec(select(SystemSetting).where(SystemSetting.key == "reminder_days_advance")).first()
    days_advance = int(setting.value) if setting else 3 # Default 3 days

    today = date.today()
    target_date = today + timedelta(days=days_advance)

    # 2. Find appointments where follow_up_date is between today and target_date (inclusive)
    # Only include scheduled or confirmed appointments (not completed or cancelled)
    # Exclude deleted appointments
    query = select(Appointment).where(
        Appointment.is_deleted == False,
        Appointment.follow_up_date >= today,
        Appointment.follow_up_date <= target_date,
        Appointment.status.in_(['scheduled', 'confirmed'])
    )
    
    # 3. Apply doctor filter if needed
    query = apply_doctor_filter(query, current_user)
    
    appointments = session.exec(query).all()
    
    # 4. Enhance with call result info
    results = []
    for appt in appointments:
        # Find latest follow-up record for this appointment
        record_query = select(FollowUpRecord).where(
            FollowUpRecord.appointment_id == appt.id
        ).order_by(FollowUpRecord.created_at.desc())
        latest_record = session.exec(record_query).first()
        
        # Use model_dump with mode='json' to handle datetime serialization
        appt_dict = appt.model_dump(mode='json')
        appt_dict['call_result'] = latest_record.status if latest_record else None
        appt_dict['call_notes'] = latest_record.notes if latest_record else None
        
        results.append(appt_dict)
        
    return results

@router.post("/record")
def record_result(record: FollowUpRecordCreate, session: Session = Depends(get_session)):
    db_record = FollowUpRecord.model_validate(record)
    session.add(db_record)
    session.commit()
    session.refresh(db_record)
    return db_record
