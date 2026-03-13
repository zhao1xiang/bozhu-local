from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from database import engine
from models import Appointment, AppointmentBase
from typing import List, Optional
from datetime import date

router = APIRouter(prefix="/appointments", tags=["appointments"])

def get_session():
    with Session(engine) as session:
        yield session

@router.post("/", response_model=Appointment)
def create_appointment(appointment: AppointmentBase, session: Session = Depends(get_session)):
    try:
        db_appointment = Appointment.model_validate(appointment)
        session.add(db_appointment)
        session.commit()
        session.refresh(db_appointment)
        return db_appointment
    except Exception as e:
        import traceback
        print("创建预约时出错:")
        print(f"数据: {appointment}")
        print(f"错误: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=422,
            detail=f"预约创建失败: {str(e)}"
        )

@router.post("/batch", response_model=List[Appointment])
def create_appointments_batch(appointments: List[AppointmentBase], session: Session = Depends(get_session)):
    try:
        db_appointments = []
        for i, appt in enumerate(appointments):
            try:
                db_appointment = Appointment.model_validate(appt)
                db_appointments.append(db_appointment)
            except Exception as e:
                import traceback
                print(f"验证第 {i+1} 个预约记录时出错:")
                print(f"数据: {appt}")
                print(f"错误: {e}")
                traceback.print_exc()
                raise HTTPException(
                    status_code=422,
                    detail=f"预约记录 {i+1} 验证失败: {str(e)}"
                )
        
        for db_appt in db_appointments:
            session.add(db_appt)
        session.commit()
        for db_appt in db_appointments:
            session.refresh(db_appt)
        return db_appointments
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print("批量创建预约时出错:")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"批量创建预约失败: {str(e)}"
        )

@router.get("/", response_model=List[Appointment])
def read_appointments(
    skip: int = 0, 
    limit: int = 100, 
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    patient_id: Optional[str] = None,
    patient_name: Optional[str] = None,
    injection_number: Optional[str] = None,
    doctor: Optional[str] = None,
    session: Session = Depends(get_session)
):
    try:
        from models.patient import Patient
        query = select(Appointment).where(Appointment.is_deleted == False)
        
        if patient_id:
            query = query.where(Appointment.patient_id == patient_id)
        
        if patient_name:
            query = query.join(Patient).where(Patient.name.contains(patient_name))
        
        if start_date:
            query = query.where(Appointment.appointment_date >= start_date)
        if end_date:
            query = query.where(Appointment.appointment_date <= end_date)
        if injection_number:
            query = query.where(Appointment.injection_number.contains(injection_number))
        if doctor:
            query = query.where(Appointment.doctor.contains(doctor))
            
        query = query.order_by(Appointment.created_at.desc(), Appointment.appointment_date.asc())
        query = query.offset(skip).limit(limit)
        appointments = session.exec(query).all()
        return appointments
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching appointments: {str(e)}"
        )

@router.get("/{appointment_id}", response_model=Appointment)
def read_appointment(appointment_id: str, session: Session = Depends(get_session)):
    appointment = session.get(Appointment, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

@router.patch("/{appointment_id}", response_model=Appointment)
def update_appointment(appointment_id: str, appointment_update: AppointmentBase, session: Session = Depends(get_session)):
    db_appointment = session.get(Appointment, appointment_id)
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    appointment_data = appointment_update.model_dump(exclude_unset=True)
    for key, value in appointment_data.items():
        setattr(db_appointment, key, value)
        
    session.add(db_appointment)
    session.commit()
    session.refresh(db_appointment)
    return db_appointment

@router.delete("/{appointment_id}")
def delete_appointment(appointment_id: str, session: Session = Depends(get_session)):
    """软删除预约"""
    appointment = session.get(Appointment, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if appointment.is_deleted:
        raise HTTPException(status_code=400, detail="Appointment already deleted")
    
    # 软删除
    appointment.is_deleted = True
    session.add(appointment)
    session.commit()
    
    return {
        "message": "Appointment deleted successfully",
        "appointment_id": appointment_id
    }

