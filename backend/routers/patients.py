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

from fastapi import UploadFile, File
from pydantic import BaseModel
import openpyxl
import io
import re

class ImportResult(BaseModel):
    success_count: int
    error_count: int
    errors: List[dict]
    duplicates: List[dict]

@router.post("/import", response_model=ImportResult)
async def import_patients(file: UploadFile = File(...), session: Session = Depends(get_session)):
    """批量导入患者"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="只支持Excel文件(.xlsx, .xls)")
    
    try:
        # 读取Excel文件
        contents = await file.read()
        wb = openpyxl.load_workbook(io.BytesIO(contents))
        ws = wb.active
        
        success_count = 0
        error_count = 0
        errors = []
        duplicates = []
        
        # 从第3行开始读取数据（第1行表头，第2行说明）
        for row_idx, row in enumerate(ws.iter_rows(min_row=3, values_only=True), start=3):
            # 跳过空行
            if not any(row):
                continue
            
            try:
                # 解析数据
                name = str(row[0]).strip() if row[0] else None
                outpatient_number = str(row[1]).strip() if row[1] else None
                medical_card_number = str(row[2]).strip() if row[2] else None
                phone = str(row[3]).strip() if row[3] else None
                diagnosis = str(row[4]).strip() if row[4] else None
                diagnosis_other = str(row[5]).strip() if row[5] else None
                drug_type = str(row[6]).strip() if row[6] else None
                drug_type_other = str(row[7]).strip() if row[7] else None
                
                # 视力数据
                left_vision = float(row[8]) if row[8] and str(row[8]).strip() else None
                right_vision = float(row[9]) if row[9] and str(row[9]).strip() else None
                left_vision_corrected = float(row[10]) if row[10] and str(row[10]).strip() else None
                right_vision_corrected = float(row[11]) if row[11] and str(row[11]).strip() else None
                
                # 注射眼别
                left_eye_str = str(row[12]).strip() if row[12] else "否"
                right_eye_str = str(row[13]).strip() if row[13] else "否"
                left_eye = left_eye_str in ["是", "True", "true", "1", "YES", "yes"]
                right_eye = right_eye_str in ["是", "True", "true", "1", "YES", "yes"]
                
                # 患者类型和针数
                patient_type = str(row[14]).strip() if row[14] else None
                injection_count = int(row[15]) if row[15] and str(row[15]).strip() else None
                
                # 数据验证
                if not name:
                    errors.append({"row": row_idx, "error": "姓名不能为空"})
                    error_count += 1
                    continue
                
                if not phone:
                    errors.append({"row": row_idx, "error": "手机号不能为空"})
                    error_count += 1
                    continue
                
                # 验证手机号格式
                if not re.match(r'^1[3-9]\d{9}$', phone):
                    errors.append({"row": row_idx, "error": f"手机号格式不正确: {phone}"})
                    error_count += 1
                    continue
                
                # 验证患者类型
                if patient_type and patient_type not in ["初治", "经治"]:
                    errors.append({"row": row_idx, "error": f"患者类型必须是'初治'或'经治': {patient_type}"})
                    error_count += 1
                    continue
                
                # 检查重复
                existing_patient = session.exec(
                    select(Patient).where(
                        Patient.is_deleted == False,
                        Patient.phone == phone
                    )
                ).first()
                
                if existing_patient:
                    duplicates.append({
                        "row": row_idx,
                        "name": name,
                        "phone": phone,
                        "existing_name": existing_patient.name
                    })
                    error_count += 1
                    continue
                
                # 创建患者
                patient_data = PatientBase(
                    name=name,
                    outpatient_number=outpatient_number,
                    medical_card_number=medical_card_number,
                    phone=phone,
                    diagnosis=diagnosis,
                    diagnosis_other=diagnosis_other,
                    drug_type=drug_type,
                    drug_type_other=drug_type_other,
                    left_vision=left_vision,
                    right_vision=right_vision,
                    left_vision_corrected=left_vision_corrected,
                    right_vision_corrected=right_vision_corrected,
                    left_eye=left_eye,
                    right_eye=right_eye,
                    patient_type=patient_type,
                    injection_count=injection_count
                )
                
                db_patient = Patient.model_validate(patient_data)
                session.add(db_patient)
                success_count += 1
                
            except Exception as e:
                errors.append({"row": row_idx, "error": str(e)})
                error_count += 1
                continue
        
        # 提交所有成功的记录
        if success_count > 0:
            session.commit()
        
        return ImportResult(
            success_count=success_count,
            error_count=error_count,
            errors=errors,
            duplicates=duplicates
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")

@router.get("/template/download")
async def download_template():
    """下载患者导入模板"""
    from fastapi.responses import FileResponse
    import os
    
    template_path = "患者批量导入模板.xlsx"
    
    # 如果模板不存在，先生成
    if not os.path.exists(template_path):
        from create_patient_template import create_patient_import_template
        create_patient_import_template()
    
    return FileResponse(
        path=template_path,
        filename="患者批量导入模板.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
