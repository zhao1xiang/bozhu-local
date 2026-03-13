from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func, text
from database import engine
from models import Appointment, Patient, FollowUpRecord
from typing import List, Dict, Any
from datetime import date, timedelta
import collections

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

def get_session():
    with Session(engine) as session:
        yield session

@router.get("/stats")
def get_dashboard_stats(session: Session = Depends(get_session)):
    today = date.today()
    
    # 1. Total Patients (exclude deleted)
    total_patients = session.exec(
        select(func.count(Patient.id)).where(Patient.is_deleted == False)
    ).one()
    
    # 2. Total Injections (Completed Appointments, exclude deleted)
    total_injections = session.exec(
        select(func.count(Appointment.id)).where(
            Appointment.status == 'completed',
            Appointment.is_deleted == False
        )
    ).one()
    
    # 3. Today's Appointments (exclude deleted)
    today_appointments = session.exec(
        select(func.count(Appointment.id)).where(
            Appointment.appointment_date == today,
            Appointment.is_deleted == False
        )
    ).one()
    
    # 4. Pending Reminders (Follow-ups due today or earlier that are not called)
    # This is a bit complex, let's just count follow-ups due in next 3 days for now as a "Pending" metric
    # Or count "Due today"
    due_today = session.exec(
        select(func.count(Appointment.id)).where(
            Appointment.next_follow_up_date == today,
            Appointment.is_deleted == False
        )
    ).one()
    
    return {
        "total_patients": total_patients,
        "total_injections": total_injections,
        "today_appointments": today_appointments,
        "due_follow_ups": due_today
    }

@router.get("/charts/trend")
def get_injection_trend(dimension: str = "month", session: Session = Depends(get_session)):
    # Last 6 months trend
    today = date.today()
    start_date = today - timedelta(days=180)
    
    query = select(Appointment).where(
        Appointment.is_deleted == False,
        Appointment.appointment_date >= start_date,
        Appointment.status == 'completed'
    ).order_by(Appointment.appointment_date)
    
    appointments = session.exec(query).all()
    
    counts = collections.defaultdict(int)
    for appt in appointments:
        if dimension == "week":
            # ISO week: YYYY-Www
            key = appt.appointment_date.strftime("%Y-W%W")
        else:
            key = appt.appointment_date.strftime("%Y-%m")
        counts[key] += 1
        
    result = [{"date": k, "count": v} for k, v in sorted(counts.items())]
    return result

@router.get("/charts/reinjection-rate")
def get_reinjection_rate(session: Session = Depends(get_session)):
    """
    计算约针率：
    - 分母：在该阶段完成过注药，且需要约下一针的患者数
    - 分子：在该阶段完成过注药，且已经约了下一针的患者数
    """
    results = {}
    
    for phase in ["强化期", "巩固期"]:
        # 找到在该阶段完成过注药的所有患者及其最高针次
        completed_query = select(
            Appointment.patient_id, 
            func.max(Appointment.injection_count).label('max_count')
        ).where(
            Appointment.is_deleted == False,
            Appointment.treatment_phase == phase,
            Appointment.status == 'completed'
        ).group_by(Appointment.patient_id)
        
        completed_in_phase = session.exec(completed_query).all()
        
        if not completed_in_phase:
            results[phase] = 0
            continue
            
        total_patients = len(completed_in_phase)
        patients_with_next_appointment = 0
        
        for patient_id, max_injection_count in completed_in_phase:
            # 检查该患者是否有下一针的预约（injection_count > max_injection_count）
            next_appointment_query = select(Appointment).where(
                Appointment.patient_id == patient_id,
                Appointment.injection_count > max_injection_count,
                Appointment.is_deleted == False,
                Appointment.status.in_(['scheduled', 'completed'])
            ).limit(1)
            
            next_appointment = session.exec(next_appointment_query).first()
            
            if next_appointment:
                patients_with_next_appointment += 1
        
        rate = round((patients_with_next_appointment / total_patients) * 100, 1) if total_patients > 0 else 0
        results[phase] = rate
    
    return results

@router.get("/charts/distribution")
def get_distributions(session: Session = Depends(get_session)):
    # 1. Drug (exclude deleted appointments)
    drug_query = select(Appointment.drug_name, func.count(Appointment.id)).where(
        Appointment.is_deleted == False
    ).group_by(Appointment.drug_name)
    drug_counts = session.exec(drug_query).all()
    drugs = [{"name": r[0] or "未填写", "value": r[1]} for r in drug_counts]
    
    # 2. Eye - 只统计有眼别数据的记录 (exclude deleted appointments)
    eye_query = select(Appointment.eye, func.count(Appointment.id)).where(
        Appointment.is_deleted == False,
        Appointment.eye.isnot(None)
    ).group_by(Appointment.eye)
    eye_counts = session.exec(eye_query).all()
    eyes = [{"name": r[0], "value": r[1]} for r in eye_counts]

    # 3. Disease (from Patient model, exclude deleted patients)
    disease_query = select(Patient.diagnosis, func.count(Patient.id)).where(
        Patient.is_deleted == False
    ).group_by(Patient.diagnosis)
    disease_counts = session.exec(disease_query).all()
    diseases = [{"name": r[0] or "未填写", "value": r[1]} for r in disease_counts]
    
    return {"drugs": drugs, "eyes": eyes, "diseases": diseases}

@router.get("/charts/doctors")
def get_doctor_workload(session: Session = Depends(get_session)):
    # Top doctors by injection count (All time, exclude deleted appointments)
    query = select(Appointment.doctor, func.count(Appointment.id)).where(
        Appointment.is_deleted == False,
        Appointment.status == 'completed'
    ).group_by(Appointment.doctor).order_by(func.count(Appointment.id).desc()).limit(10)
    counts = session.exec(query).all()
    
    result = [{"name": r[0] or "Unknown", "value": r[1]} for r in counts]
    return result
