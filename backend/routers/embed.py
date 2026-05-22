"""
iframe 嵌入预约接口
GET  /embed/verify   - 验证签名并返回患者+预约数据
POST /embed/save     - 保存患者（upsert）和预约记录
"""
import hashlib
import base64
import json
import time
import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from database import engine
from models import Patient, Appointment, AppointmentBase
from models.patient import PatientBase
from models.system_setting import SystemSetting
from models.embed_log import EmbedLog
from typing import List, Optional
from datetime import date
import uuid
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/embed", tags=["embed"])

TIMESTAMP_EXPIRE_SECONDS = 300  # 5分钟


def get_session():
    with Session(engine, expire_on_commit=False) as session:
        yield session


def get_secret_key(session: Session) -> str:
    setting = session.exec(
        select(SystemSetting).where(SystemSetting.key == "embed_secret_key")
    ).first()
    return setting.value if setting else "f9A7xK2mQ8vZrP4sT1uWc6YhN3bD5eL0"


def verify_sign(data: str, sign: str, secret_key: str) -> bool:
    expected = hashlib.md5(f"{data}{secret_key}".encode()).hexdigest()
    return expected == sign


def decode_data(data: str) -> dict:
    try:
        decoded = base64.b64decode(data).decode("utf-8")
        return json.loads(decoded)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"data 解码失败: {e}")


@router.post("/generate-link")
def generate_embed_link(
    body: dict,
    request: Request,
    session: Session = Depends(get_session),
):
    """根据 payload 生成带签名的 embed 链接"""
    from urllib.parse import quote
    payload = body.get("payload", {})
    if not payload.get("timestamp"):
        payload["timestamp"] = int(time.time())

    secret_key = get_secret_key(session)
    data = base64.b64encode(
        json.dumps(payload, ensure_ascii=False).encode()
    ).decode()
    sign = hashlib.md5(f"{data}{secret_key}".encode()).hexdigest()

    # 构建 URL，使用请求的 host
    base_url = str(request.base_url).rstrip("/")
    url = f"{base_url}/embed/appointment?data={quote(data)}&sign={sign}"
    return {"url": url, "data": data, "sign": sign}


@router.get("/verify-plain")
def verify_plain(
    name: str = "",
    outpatient_number: str = "",
    phone: str = "",
    diagnosis: str = "",
    drug_name: str = "",
    eye: str = "",
    injection_count: int = 0,
    doctor: str = "",
    request: Request = None,
    session: Session = Depends(get_session),
):
    """明文参数接口，不需要签名验证"""
    # 记录调用日志
    import json as _json
    params_dict = {
        "name": name, "outpatient_number": outpatient_number, "phone": phone,
        "diagnosis": diagnosis, "drug_name": drug_name, "eye": eye,
        "injection_count": injection_count, "doctor": doctor,
    }
    client_ip = request.client.host if request else None
    full_url = str(request.url) if request else None
    log = EmbedLog(
        call_type="verify-plain",
        url=full_url,
        params=_json.dumps(params_dict, ensure_ascii=False),
        outpatient_number=outpatient_number or None,
        patient_name=name or None,
        client_ip=client_ip,
        success=True,
    )
    session.add(log)
    session.commit()
    payload = {
        "name": name,
        "outpatient_number": outpatient_number,
        "phone": phone,
        "diagnosis": diagnosis,
        "drug_name": drug_name,
        "eye": eye,
        "injection_count": injection_count,
        "doctor": doctor,
        "patient_type": "经治" if injection_count >= 1 else "初治",
    }

    patient = None
    appointments = []
    if outpatient_number:
        patient = session.exec(
            select(Patient).where(
                Patient.outpatient_number == outpatient_number,
                Patient.is_deleted == False,
            )
        ).first()
        if patient:
            q = select(Appointment).where(
                Appointment.patient_id == patient.id,
                Appointment.is_deleted == False,
            )
            if eye and eye != "双眼":
                q = q.where(Appointment.eye == eye)
            q = q.order_by(Appointment.appointment_date)
            appointments = session.exec(q).all()

    return {"patient": patient, "appointments": appointments, "payload": payload}


@router.get("/verify")
def verify_and_get_data(
    data: str,
    sign: str,
    request: Request,
    session: Session = Depends(get_session),
):
    """
    验证签名，返回患者信息和已有预约记录
    """
    import json as _json
    client_ip = request.client.host if request else None
    full_url = str(request.url) if request else None
    secret_key = get_secret_key(session)

    # URL 解码后 + 会变成空格，需要还原
    data = data.replace(" ", "+")

    # 1. 验证签名
    if not verify_sign(data, sign, secret_key):
        log = EmbedLog(call_type="verify", url=full_url, params=data,
                       client_ip=client_ip, success=False, error_msg="签名验证失败")
        session.add(log); session.commit()
        raise HTTPException(status_code=403, detail="签名验证失败")

    # 2. 解码数据
    payload = decode_data(data)

    # 3. 验证时间戳
    ts = payload.get("timestamp", 0)
    if abs(time.time() - int(ts)) > TIMESTAMP_EXPIRE_SECONDS:
        log = EmbedLog(call_type="verify", url=full_url, params=_json.dumps(payload, ensure_ascii=False),
                       client_ip=client_ip, success=False, error_msg="请求已过期")
        session.add(log); session.commit()
        raise HTTPException(status_code=400, detail="请求已过期")

    # 记录成功日志
    log = EmbedLog(
        call_type="verify",
        url=full_url,
        params=_json.dumps(payload, ensure_ascii=False),
        outpatient_number=payload.get("outpatient_number") or None,
        patient_name=payload.get("name") or None,
        client_ip=client_ip,
        success=True,
    )
    session.add(log)
    session.commit()

    outpatient_number = payload.get("outpatient_number")
    eye = payload.get("eye")  # 左眼/右眼/双眼

    # 4. 查询患者
    patient = None
    appointments = []
    if outpatient_number:
        patient = session.exec(
            select(Patient).where(
                Patient.outpatient_number == outpatient_number,
                Patient.is_deleted == False,
            )
        ).first()

        if patient:
            # 查询该患者对应眼别的预约记录
            q = select(Appointment).where(
                Appointment.patient_id == patient.id,
                Appointment.is_deleted == False,
            )
            if eye and eye != "双眼":
                q = q.where(Appointment.eye == eye)
            q = q.order_by(Appointment.appointment_date)
            appointments = session.exec(q).all()

    return {
        "patient": patient,
        "appointments": appointments,
        "payload": payload,
    }


@router.post("/save")
def save_patient_and_appointments(
    body: dict,
    session: Session = Depends(get_session),
):
    """
    upsert 患者，upsert 预约记录
    body: { patient: {...}, appointments: [...] }
    """
    from sqlalchemy import text as sa_text

    conn = session.connection()
    patient_data = body.get("patient", {})
    appointments_data = body.get("appointments", [])
    outpatient_number = patient_data.get("outpatient_number")
    now_str = datetime.now(timezone.utc).isoformat()

    # 查患者
    patient_id = None
    if outpatient_number:
        row = conn.execute(sa_text(
            "SELECT id FROM patient WHERE outpatient_number=:n AND is_deleted=0"
        ), {"n": outpatient_number}).first()
        if row:
            patient_id = row[0]

    if patient_id:
        # 更新患者
        eye = patient_data.get("eye", "")
        phone_new = patient_data.get("phone", "") or ""
        # 过滤"无"值
        if phone_new in ("无", "null", "undefined"):
            phone_new = ""

        update_params = {
            "name": patient_data.get("name", ""),
            "diagnosis": patient_data.get("diagnosis") or "",
            "drug_type": patient_data.get("drug_name") or "",
            "left_eye": 1 if eye in ["左眼", "双眼"] else 0,
            "right_eye": 1 if eye in ["右眼", "双眼"] else 0,
            "patient_type": patient_data.get("patient_type") or "",
            "doctor": patient_data.get("doctor") or None,
            "updated_at": now_str,
            "id": patient_id,
        }

        if phone_new:
            # 检查新 phone 是否被其他患者占用
            existing = conn.execute(sa_text(
                "SELECT id FROM patient WHERE phone=:p AND is_deleted=0 AND id!=:id"
            ), {"p": phone_new, "id": patient_id}).first()
            if not existing:
                update_params["phone"] = phone_new
                conn.execute(sa_text("""
                    UPDATE patient SET name=:name, diagnosis=:diagnosis, drug_type=:drug_type,
                        left_eye=:left_eye, right_eye=:right_eye, patient_type=:patient_type,
                        doctor=:doctor, phone=:phone, updated_at=:updated_at
                    WHERE id=:id
                """), update_params)
            else:
                del update_params["phone"]
                conn.execute(sa_text("""
                    UPDATE patient SET name=:name, diagnosis=:diagnosis, drug_type=:drug_type,
                        left_eye=:left_eye, right_eye=:right_eye, patient_type=:patient_type,
                        doctor=:doctor, updated_at=:updated_at
                    WHERE id=:id
                """), update_params)
        else:
            conn.execute(sa_text("""
                UPDATE patient SET name=:name, diagnosis=:diagnosis, drug_type=:drug_type,
                    left_eye=:left_eye, right_eye=:right_eye, patient_type=:patient_type,
                    doctor=:doctor, updated_at=:updated_at
                WHERE id=:id
            """), update_params)
    else:
        # 新建患者
        phone = patient_data.get("phone") or ""
        if phone in ("无", "null", "undefined"):
            phone = ""
        if phone:
            row = conn.execute(sa_text(
                "SELECT id FROM patient WHERE phone=:p AND is_deleted=0"
            ), {"p": phone}).first()
            if row:
                phone = ""  # 已被占用，存 NULL

        patient_id = str(uuid.uuid4())
        eye = patient_data.get("eye", "")
        inj = patient_data.get("injection_count")
        doctor_val = patient_data.get("doctor") or None
        conn.execute(sa_text("""
            INSERT INTO patient (id, name, outpatient_number, phone, diagnosis, drug_type,
                left_eye, right_eye, patient_type, injection_count, doctor, status, is_deleted,
                created_at, updated_at)
            VALUES (:id, :name, :outpatient_number, :phone, :diagnosis, :drug_type,
                :left_eye, :right_eye, :patient_type, :injection_count, :doctor, 'active', 0,
                :created_at, :updated_at)
        """), {
            "id": patient_id,
            "name": patient_data.get("name", ""),
            "outpatient_number": outpatient_number,
            "phone": phone if phone else None,
            "diagnosis": patient_data.get("diagnosis"),
            "drug_type": patient_data.get("drug_name"),
            "left_eye": 1 if eye in ["左眼", "双眼"] else 0,
            "right_eye": 1 if eye in ["右眼", "双眼"] else 0,
            "patient_type": patient_data.get("patient_type"),
            "injection_count": inj if patient_data.get("patient_type") == "经治" else None,
            "doctor": doctor_val,
            "created_at": now_str,
            "updated_at": now_str,
        })

    # upsert 预约
    for appt_data in appointments_data:
        for date_field in ["appointment_date", "follow_up_date", "next_follow_up_date"]:
            if appt_data.get(date_field) and isinstance(appt_data[date_field], str):
                try:
                    appt_data[date_field] = str(date.fromisoformat(appt_data[date_field]))
                except Exception:
                    appt_data[date_field] = None

        injection_count = appt_data.get("injection_count")
        appt_id = appt_data.get("id")

        existing_id = None
        if appt_id:
            row = conn.execute(sa_text("SELECT id FROM appointment WHERE id=:id"), {"id": appt_id}).first()
            if row:
                existing_id = appt_id
        if not existing_id and injection_count is not None:
            row = conn.execute(sa_text(
                "SELECT id FROM appointment WHERE patient_id=:pid AND injection_count=:cnt AND is_deleted=0"
            ), {"pid": patient_id, "cnt": injection_count}).first()
            if row:
                existing_id = row[0]

        if existing_id:
            conn.execute(sa_text("""
                UPDATE appointment SET
                    appointment_date=:appointment_date, follow_up_date=:follow_up_date,
                    time_slot=:time_slot, condition_status=:condition_status,
                    treatment_phase=:treatment_phase, eye=:eye, drug_name=:drug_name,
                    doctor=:doctor, patient_id=:patient_id, updated_at=:updated_at
                WHERE id=:id
            """), {
                "appointment_date": appt_data.get("appointment_date"),
                "follow_up_date": appt_data.get("follow_up_date"),
                "time_slot": appt_data.get("time_slot"),
                "condition_status": appt_data.get("condition_status"),
                "treatment_phase": appt_data.get("treatment_phase"),
                "eye": appt_data.get("eye"),
                "drug_name": appt_data.get("drug_name"),
                "doctor": appt_data.get("doctor"),
                "patient_id": patient_id,
                "updated_at": now_str,
                "id": existing_id,
            })
        else:
            new_id = str(uuid.uuid4())
            conn.execute(sa_text("""
                INSERT INTO appointment (id, patient_id, appointment_date, follow_up_date,
                    time_slot, condition_status, treatment_phase, eye, drug_name, doctor,
                    injection_count, source, status, is_deleted, created_at, updated_at)
                VALUES (:id, :patient_id, :appointment_date, :follow_up_date,
                    :time_slot, :condition_status, :treatment_phase, :eye, :drug_name, :doctor,
                    :injection_count, :source, 'scheduled', 0, :created_at, :updated_at)
            """), {
                "id": new_id,
                "patient_id": patient_id,
                "appointment_date": appt_data.get("appointment_date"),
                "follow_up_date": appt_data.get("follow_up_date"),
                "time_slot": appt_data.get("time_slot"),
                "condition_status": appt_data.get("condition_status"),
                "treatment_phase": appt_data.get("treatment_phase"),
                "eye": appt_data.get("eye"),
                "drug_name": appt_data.get("drug_name"),
                "doctor": appt_data.get("doctor"),
                "injection_count": injection_count,
                "source": appt_data.get("source", "embed"),
                "created_at": now_str,
                "updated_at": now_str,
            })

    session.commit()

    # 重新查询返回
    patient_row = session.exec(
        select(Patient).where(Patient.id == patient_id)
    ).first()
    appt_rows = session.exec(
        select(Appointment).where(
            Appointment.patient_id == patient_id,
            Appointment.is_deleted == False,
        )
    ).all()

    return {"patient": patient_row, "appointments": appt_rows}
