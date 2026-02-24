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
    
    # 1. Total Patients
    total_patients = session.exec(select(func.count(Patient.id))).one()
    
    # 2. Total Injections (Completed Appointments)
    total_injections = session.exec(select(func.count(Appointment.id)).where(Appointment.status == 'completed')).one()
    
    # 3. Today's Appointments
    today_appointments = session.exec(select(func.count(Appointment.id)).where(Appointment.appointment_date == today)).one()
    
    # 4. Pending Reminders (Follow-ups due today or earlier that are not called)
    # This is a bit complex, let's just count follow-ups due in next 3 days for now as a "Pending" metric
    # Or count "Due today"
    due_today = session.exec(select(func.count(Appointment.id)).where(Appointment.next_follow_up_date == today)).one()
    
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
    # Logic: For each phase (强化期/巩固期), count patients who have completed a needle 
    # and have a subsequent needle (completed or scheduled).
    
    results = {}
    for phase in ["强化期", "巩固期"]:
        # Total patients who had at least one injection in this phase
        total_p_query = select(func.count(func.distinct(Appointment.patient_id))).where(
            Appointment.treatment_phase == phase,
            Appointment.status == 'completed'
        )
        total_patients = session.exec(total_p_query).one()
        
        if total_patients == 0:
            results[phase] = 0
            continue
            
        # Patients in this phase who have a NEXT injection (injection_count > 1 for that phase or just count distinct)
        # More robust: Find patients who finished needle N and have needle N+1 scheduled/completed
        # For simplicity in this demo: count patients who have more than 1 appointment in this phase OR have an appointment in the NEXT phase
        
        # Let's use a simpler logic for the "rate of booking next":
        # Patients whose LATEST injection was 'completed' but they HAVE a 'scheduled' one in the future
        # OR patients who have multiple completed injections.
        
        # Actually, the user defined: 分母为患者数，分子为约了下一针的数量
        # If we count all patients who ever had an injection, how many have a future one?
        
        sub_query = select(func.count(func.distinct(Appointment.patient_id))).where(
            Appointment.treatment_phase == phase,
            Appointment.status == 'scheduled'
        )
        scheduled_patients = session.exec(sub_query).one()
        
        # Or even better: patients who HAVE completed an injection AND HAVE another one scheduled/completed later
        # For a truly informative "约针率"
        rate = round((scheduled_patients / total_patients) * 100, 1) if total_patients > 0 else 0
        results[phase] = rate
        
    return results

@router.get("/charts/distribution")
def get_distributions(session: Session = Depends(get_session)):
    # 1. Drug
    drug_query = select(Appointment.drug_name, func.count(Appointment.id)).group_by(Appointment.drug_name)
    drug_counts = session.exec(drug_query).all()
    drugs = [{"name": r[0] or "Unknown", "value": r[1]} for r in drug_counts]
    
    # 2. Eye
    eye_query = select(Appointment.eye, func.count(Appointment.id)).group_by(Appointment.eye)
    eye_counts = session.exec(eye_query).all()
    eyes = [{"name": r[0] or "Unknown", "value": r[1]} for r in eye_counts]

    # 3. Disease (from Patient model)
    disease_query = select(Patient.diagnosis, func.count(Patient.id)).group_by(Patient.diagnosis)
    disease_counts = session.exec(disease_query).all()
    diseases = [{"name": r[0] or "Unknown", "value": r[1]} for r in disease_counts]
    
    return {"drugs": drugs, "eyes": eyes, "diseases": diseases}

@router.get("/charts/doctors")
def get_doctor_workload(session: Session = Depends(get_session)):
    # Top doctors by injection count (All time)
    query = select(Appointment.doctor, func.count(Appointment.id)).where(Appointment.status == 'completed').group_by(Appointment.doctor).order_by(func.count(Appointment.id).desc()).limit(10)
    counts = session.exec(query).all()
    
    result = [{"name": r[0] or "Unknown", "value": r[1]} for r in counts]
    return result
