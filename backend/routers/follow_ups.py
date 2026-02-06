from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from database import engine
from models import Appointment, FollowUpRecord, FollowUpRecordCreate, SystemSetting, Patient
from typing import List, Optional
from datetime import date, timedelta

router = APIRouter(prefix="/follow-ups", tags=["follow-ups"])

def get_session():
    with Session(engine) as session:
        yield session

@router.get("/reminders")
def get_reminders(session: Session = Depends(get_session)):
    # 1. Get advance days setting
    setting = session.exec(select(SystemSetting).where(SystemSetting.key == "reminder_days_advance")).first()
    days_advance = int(setting.value) if setting else 3 # Default 3 days

    today = date.today()
    target_date = today + timedelta(days=days_advance)

    # 2. Find appointments where next_follow_up_date is between today and target_date (inclusive)
    query = select(Appointment).where(
        Appointment.next_follow_up_date >= today,
        Appointment.next_follow_up_date <= target_date
    )
    appointments = session.exec(query).all()
    
    # 3. Enhance with call result info
    results = []
    for appt in appointments:
        # Find latest follow-up record for this appointment
        # Assuming one appointment might be called multiple times? Usually yes.
        # We want the latest status.
        record_query = select(FollowUpRecord).where(FollowUpRecord.appointment_id == appt.id).order_by(FollowUpRecord.created_at.desc())
        latest_record = session.exec(record_query).first()
        
        appt_dict = appt.model_dump()
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
