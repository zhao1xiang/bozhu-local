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
    # Check for duplicates
    existing_patient = session.exec(
        select(Patient).where(
            (Patient.outpatient_number == patient.outpatient_number) | 
            (Patient.phone == patient.phone)
        )
    ).first()
    
    if existing_patient:
        raise HTTPException(
            status_code=409, 
            detail={
                "message": "Patient already exists",
                "patient": existing_patient.model_dump()
            }
        )
        
    db_patient = Patient.model_validate(patient)
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    return db_patient

@router.get("/", response_model=List[Patient])
def read_patients(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    patients = session.exec(
        select(Patient)
        .order_by(Patient.created_at.desc())
        .offset(skip).limit(limit)
    ).all()
    return patients

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
