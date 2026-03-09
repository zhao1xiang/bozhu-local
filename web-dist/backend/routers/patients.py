from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import engine
from models import Patient, PatientBase
from typing import List

router = APIRouter(prefix="/patients", tags=["patients"])

def get_session():
    with Session(engine) as session:
        yield session

@router.post("/", response_model=Patient)
def create_patient(patient: PatientBase, session: Session = Depends(get_session)):
    # Check for duplicates (exclude deleted patients)
    # Only check phone for duplicates since outpatient_number is now optional
    existing_patient = session.exec(
        select(Patient).where(
            Patient.is_deleted == False,
            Patient.phone == patient.phone
        )
    ).first()
    
    if existing_patient:
        raise HTTPException(
            status_code=409, 
            detail={
                "message": "Patient already exists",
                "patient": {
                    "id": existing_patient.id,
                    "name": existing_patient.name,
                    "outpatient_number": existing_patient.outpatient_number,
                    "phone": existing_patient.phone
                }
            }
        )
        
    db_patient = Patient.model_validate(patient)
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    return db_patient

@router.get("/", response_model=List[Patient])
def read_patients(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    try:
        patients = session.exec(
            select(Patient)
            .where(Patient.is_deleted == False)
            .order_by(Patient.created_at.desc())
            .offset(skip).limit(limit)
        ).all()
        return patients
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching patients: {str(e)}"
        )

@router.get("/{patient_id}", response_model=Patient)
def read_patient(patient_id: str, session: Session = Depends(get_session)):
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.put("/{patient_id}", response_model=Patient)
def update_patient(patient_id: str, patient: PatientBase, session: Session = Depends(get_session)):
    db_patient = session.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient_data = patient.model_dump(exclude_unset=True)
    for key, value in patient_data.items():
        setattr(db_patient, key, value)
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    return db_patient

@router.delete("/{patient_id}")
def delete_patient(patient_id: str, session: Session = Depends(get_session)):
    """软删除患者及其所有预约"""
    from models import Appointment
    
    # 查找患者
    db_patient = session.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    if db_patient.is_deleted:
        raise HTTPException(status_code=400, detail="Patient already deleted")
    
    # 软删除患者
    db_patient.is_deleted = True
    session.add(db_patient)
    
    # 软删除该患者的所有预约
    appointments = session.exec(
        select(Appointment).where(
            Appointment.patient_id == patient_id,
            Appointment.is_deleted == False
        )
    ).all()
    
    deleted_count = 0
    for appointment in appointments:
        appointment.is_deleted = True
        session.add(appointment)
        deleted_count += 1
    
    session.commit()
    
    return {
        "message": "Patient and related appointments deleted successfully",
        "patient_id": patient_id,
        "deleted_appointments_count": deleted_count
    }
