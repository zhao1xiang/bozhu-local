from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from database import engine
from models import Patient, PatientBase
from models.data_dictionary import DataDictionary
from models.user import User
from typing import List, Optional
from jose import jwt
from security import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/patients", tags=["patients"])

def get_session():
    with Session(engine) as session:
        yield session


def get_optional_user(request: Request, session: Session = Depends(get_session)) -> Optional[User]:
    """获取当前用户，无 token 时返回 None 而不报错"""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth[7:]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        if not username:
            return None
        return session.exec(select(User).where(User.username == username)).first()
    except Exception:
        return None


def get_ward_doctor_values(wards: str, session: Session) -> Optional[List[str]]:
    """根据病区列表获取对应的医生 value 列表
    返回 None 表示不过滤（admin），返回列表（可能为空）表示按病区过滤
    """
    if not wards:
        return None
    ward_list = [w.strip() for w in wards.split(',') if w.strip()]
    if not ward_list:
        return None
    try:
        doctors = session.exec(
            select(DataDictionary).where(
                DataDictionary.category == 'doctor',
                DataDictionary.is_active == True,
            )
        ).all()
        # 返回属于该病区的医生列表（可能为空，表示该病区没有配置医生）
        return [d.value for d in doctors if getattr(d, 'ward', None) and any(w in str(d.ward).split(',') for w in ward_list)]
    except Exception:
        return []

@router.post("/", response_model=Patient)
def create_patient(patient: PatientBase, session: Session = Depends(get_session)):
    # 仅当手机号有值时检查重复
    if patient.phone:
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
def read_patients(
    skip: int = 0, limit: int = 99999,
    outpatient_number: str = None,
    session: Session = Depends(get_session),
    current_user: Optional[User] = Depends(get_optional_user),
):
    try:
        from models import Appointment
        q = select(Patient).where(Patient.is_deleted == False)
        if outpatient_number:
            q = q.where(Patient.outpatient_number == outpatient_number)

        # 病区过滤：ward 账号只能看自己病区医生的患者
        role = getattr(current_user, 'role', 'admin')
        wards = getattr(current_user, 'wards', None)
        if role != 'admin' and wards:
            doctor_values = get_ward_doctor_values(wards, session)
            if doctor_values is not None:
                # 找出有注药医生的患者（取最新预约的医生）
                # 策略：患者的最新预约的 doctor 在病区医生列表里，或者患者没有任何预约（无病区，所有人可见）
                all_patients = session.exec(q.order_by(Patient.created_at.desc()).offset(skip).limit(limit)).all()
                filtered = []
                for p in all_patients:
                    latest_appt = session.exec(
                        select(Appointment).where(
                            Appointment.patient_id == p.id,
                            Appointment.is_deleted == False,
                            Appointment.doctor != None,
                        ).order_by(Appointment.created_at.desc())
                    ).first()
                    if latest_appt is None:
                        # 没有注药医生，所有病区可见
                        filtered.append(p)
                    elif latest_appt.doctor in doctor_values:
                        filtered.append(p)
                return filtered

        patients = session.exec(q.order_by(Patient.created_at.desc()).offset(skip).limit(limit)).all()
        return patients
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching patients: {str(e)}")

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
    """批量导入患者（支持同时导入预约）"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="只支持Excel文件(.xlsx, .xls)")

    try:
        contents = await file.read()
        wb = openpyxl.load_workbook(io.BytesIO(contents))
        ws = wb.active

        success_count = 0
        error_count = 0
        errors = []
        duplicates = []

        for row_idx, row in enumerate(ws.iter_rows(min_row=3, values_only=True), start=3):
            if not any(row):
                continue

            try:
                # 患者字段（列 0-16）
                name = str(row[0]).strip() if row[0] else None
                outpatient_number = str(row[1]).strip() if row[1] else None
                medical_card_number = str(row[2]).strip() if row[2] else None
                phone = str(row[3]).strip() if row[3] else None
                diagnosis = str(row[4]).strip() if row[4] else None
                diagnosis_other = str(row[5]).strip() if row[5] else None
                drug_type = str(row[6]).strip() if row[6] else None
                drug_type_other = str(row[7]).strip() if row[7] else None
                left_vision = str(row[8]).strip() if row[8] and str(row[8]).strip() else None
                right_vision = str(row[9]).strip() if row[9] and str(row[9]).strip() else None
                left_vision_corrected = str(row[10]).strip() if row[10] and str(row[10]).strip() else None
                right_vision_corrected = str(row[11]).strip() if row[11] and str(row[11]).strip() else None
                left_eye_str = str(row[12]).strip() if row[12] else "否"
                right_eye_str = str(row[13]).strip() if row[13] else "否"
                left_eye = left_eye_str in ["是", "True", "true", "1", "YES", "yes"]
                right_eye = right_eye_str in ["是", "True", "true", "1", "YES", "yes"]
                patient_type = str(row[14]).strip() if row[14] else None
                injection_count = int(row[15]) if row[15] and str(row[15]).strip() else None
                remarks = str(row[16]).strip() if row[16] else None

                # 预约字段（列 17-26，可选）
                appt_date_raw = row[17] if len(row) > 17 else None
                appt_eye = str(row[18]).strip() if len(row) > 18 and row[18] else None
                appt_drug = str(row[19]).strip() if len(row) > 19 and row[19] else None
                appt_doctor = str(row[20]).strip() if len(row) > 20 and row[20] else None
                appt_cost_type = str(row[21]).strip() if len(row) > 21 and row[21] else None
                appt_injection_count = int(row[22]) if len(row) > 22 and row[22] and str(row[22]).strip() else None
                appt_treatment_phase = str(row[23]).strip() if len(row) > 23 and row[23] else None
                appt_time_slot = str(row[24]).strip() if len(row) > 24 and row[24] else "上午"
                appt_condition_status = str(row[25]).strip() if len(row) > 25 and row[25] else None
                appt_notes = str(row[26]).strip() if len(row) > 26 and row[26] else None

                # 解析预约日期
                appt_date = None
                if appt_date_raw:
                    from datetime import date as date_type, datetime as dt_type
                    if isinstance(appt_date_raw, date_type):
                        appt_date = appt_date_raw
                    else:
                        try:
                            appt_date = dt_type.strptime(str(appt_date_raw).strip(), "%Y-%m-%d").date()
                        except Exception:
                            pass

                # 数据验证
                if not name:
                    errors.append({"row": row_idx, "error": "姓名不能为空"})
                    error_count += 1
                    continue

                if patient_type and patient_type not in ["初治", "经治"]:
                    errors.append({"row": row_idx, "error": f"患者类型必须是'初治'或'经治': {patient_type}"})
                    error_count += 1
                    continue

                # 检查重复（按手机号，仅当手机号有值时）
                existing_patient = None
                if phone:
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
                        "phone": phone or "",
                        "existing_name": existing_patient.name
                    })
                    error_count += 1
                    continue

                # 创建患者
                from models.appointment import Appointment as ApptModel
                import uuid as uuid_mod

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
                    injection_count=injection_count,
                    remarks=remarks
                )
                db_patient = Patient.model_validate(patient_data)
                session.add(db_patient)
                session.flush()  # 获取 patient id

                # 如果有预约日期，创建预约
                if appt_date:
                    appt = ApptModel(
                        id=str(uuid_mod.uuid4()),
                        patient_id=db_patient.id,
                        appointment_date=appt_date,
                        eye=appt_eye,
                        drug_name=appt_drug,
                        doctor=appt_doctor,
                        cost_type=appt_cost_type,
                        injection_count=appt_injection_count,
                        treatment_phase=appt_treatment_phase,
                        time_slot=appt_time_slot,
                        condition_status=appt_condition_status,
                        notes=appt_notes,
                        status="scheduled",
                    )
                    session.add(appt)

                success_count += 1

            except Exception as e:
                errors.append({"row": row_idx, "error": str(e)})
                error_count += 1
                continue

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
