from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select, func, distinct, or_
from database import engine
from models import Appointment, Patient, FollowUpRecord
from models.user import User
from models.data_dictionary import DataDictionary
from security import get_current_user
from datetime import date, timedelta
import collections
from typing import Optional
from jose import jwt
from security import SECRET_KEY

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


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


def apply_doctor_filter(query, current_user: Optional[User], session: Session):
    """
    医生账号只看自己名下的预约（doctor 为空的预约所有人可见）
    admin 不过滤
    """
    from models.data_dictionary import DataDictionary
    
    role = getattr(current_user, 'role', 'admin')
    bound_doctor = getattr(current_user, 'doctor', None)
    user_wards = getattr(current_user, 'wards', None)
    
    if role != 'admin':
        # 如果医生配置了分组，查询该分组内所有医生的预约
        if user_wards:
            # user_wards 格式: "1,2,3" (分组编号列表)
            ward_list = [w.strip() for w in user_wards.split(',') if w.strip()]
            if ward_list:
                # 查找所有分组包含这些编号的医生
                doctors_in_wards = session.exec(
                    select(DataDictionary).where(
                        DataDictionary.category == 'doctor',
                        DataDictionary.is_active == True
                    )
                ).all()
                
                # 过滤出分组包含指定编号的医生
                matching_doctors = []
                for doc in doctors_in_wards:
                    doc_wards = [w.strip() for w in (doc.ward or '').split(',') if w.strip()]
                    if any(w in ward_list for w in doc_wards):
                        matching_doctors.append(doc.value)
                
                if matching_doctors:
                    query = query.where(
                        or_(
                            Appointment.doctor == None,
                            Appointment.doctor == '',
                            Appointment.doctor.in_(matching_doctors),
                        )
                    )
                else:
                    # 分组内没有医生，返回空结果
                    query = query.where(Appointment.doctor == None)
            else:
                # 分组为空，返回空结果
                query = query.where(Appointment.doctor == None)
        # 如果医生没有配置分组，按医生名字查询
        elif bound_doctor:
            query = query.where(
                or_(
                    Appointment.doctor == None,
                    Appointment.doctor == '',
                    Appointment.doctor == bound_doctor,
                )
            )
        else:
            # 既没有分组也没有绑定医生，返回空结果
            query = query.where(Appointment.doctor == None)
    return query


def apply_patient_doctor_filter(query, current_user: Optional[User], session: Session):
    """
    对患者表的过滤：医生账号只看自己名下的患者（patient.doctor 为空的患者所有人可见）
    """
    from models.data_dictionary import DataDictionary
    
    role = getattr(current_user, 'role', 'admin')
    bound_doctor = getattr(current_user, 'doctor', None)
    user_wards = getattr(current_user, 'wards', None)
    
    if role != 'admin':
        # 如果医生配置了分组，查询该分组内所有医生的患者
        if user_wards:
            # user_wards 格式: "1,2,3" (分组编号列表)
            ward_list = [w.strip() for w in user_wards.split(',') if w.strip()]
            if ward_list:
                # 查找所有分组包含这些编号的医生
                doctors_in_wards = session.exec(
                    select(DataDictionary).where(
                        DataDictionary.category == 'doctor',
                        DataDictionary.is_active == True
                    )
                ).all()
                
                # 过滤出分组包含指定编号的医生
                matching_doctors = []
                for doc in doctors_in_wards:
                    doc_wards = [w.strip() for w in (doc.ward or '').split(',') if w.strip()]
                    if any(w in ward_list for w in doc_wards):
                        matching_doctors.append(doc.value)
                
                if matching_doctors:
                    query = query.where(Patient.doctor.in_(matching_doctors))
                else:
                    # 分组内没有医生，返回空结果
                    query = query.where(Patient.doctor == None)
            else:
                # 分组为空，返回空结果
                query = query.where(Patient.doctor == None)
        # 如果医生没有配置分组，按医生名字查询
        elif bound_doctor:
            query = query.where(
                or_(
                    Patient.doctor == None,
                    Patient.doctor == '',
                    Patient.doctor == bound_doctor,
                )
            )
        else:
            # 既没有分组也没有绑定医生，返回空结果
            query = query.where(Patient.doctor == None)
    return query


@router.get("/stats")
def get_dashboard_stats(
    session: Session = Depends(get_session),
    current_user: Optional[User] = Depends(get_optional_user),
):
    today = date.today()

    # 累计患者数
    patient_query = select(func.count(Patient.id)).where(Patient.is_deleted == False)
    patient_query = apply_patient_doctor_filter(patient_query, current_user, session)
    total_patients = session.exec(patient_query).one()

    # 累计完成注药
    injection_query = select(func.count(Appointment.id)).where(
        Appointment.status == 'completed',
        Appointment.is_deleted == False
    )
    injection_query = apply_doctor_filter(injection_query, current_user, session)
    total_injections = session.exec(injection_query).one()

    # 今日预约
    today_query = select(func.count(Appointment.id)).where(
        Appointment.appointment_date == today,
        Appointment.is_deleted == False
    )
    today_query = apply_doctor_filter(today_query, current_user, session)
    today_appointments = session.exec(today_query).one()

    # 复诊提醒（今日到期）
    due_query = select(func.count(Appointment.id)).where(
        Appointment.next_follow_up_date == today,
        Appointment.is_deleted == False
    )
    due_query = apply_doctor_filter(due_query, current_user, session)
    due_today = session.exec(due_query).one()

    return {
        "total_patients": total_patients,
        "total_injections": total_injections,
        "today_appointments": today_appointments,
        "due_follow_ups": due_today
    }


@router.get("/charts/trend")
def get_injection_trend(
    dimension: str = "month",
    session: Session = Depends(get_session),
    current_user: Optional[User] = Depends(get_optional_user),
):
    today = date.today()
    start_date = today - timedelta(days=180)

    query = select(Appointment).where(
        Appointment.is_deleted == False,
        Appointment.appointment_date >= start_date,
        Appointment.status == 'completed'
    )
    query = apply_doctor_filter(query, current_user, session)
    appointments = session.exec(query.order_by(Appointment.appointment_date)).all()

    counts = collections.defaultdict(int)
    for appt in appointments:
        if dimension == "week":
            key = appt.appointment_date.strftime("%Y-W%W")
        else:
            key = appt.appointment_date.strftime("%Y-%m")
        counts[key] += 1

    return [{"date": k, "count": v} for k, v in sorted(counts.items())]


@router.get("/charts/reinjection-rate")
def get_reinjection_rate(
    session: Session = Depends(get_session),
    current_user: Optional[User] = Depends(get_optional_user),
):
    # 分母：有过预约的建档患者数
    denom_query = select(func.count(distinct(Appointment.patient_id))).where(
        Appointment.is_deleted == False
    )
    denom_query = apply_doctor_filter(denom_query, current_user, session)
    denominator = session.exec(denom_query).one() or 0

    if denominator == 0:
        return {"强化期": 0, "巩固期": 0}

    # 强化期条数
    qh_query = select(func.count(Appointment.id)).where(
        Appointment.is_deleted == False,
        Appointment.treatment_phase == "强化期",
    )
    qh_query = apply_doctor_filter(qh_query, current_user, session)
    qh_count = session.exec(qh_query).one() or 0

    # 巩固期条数
    gj_appt_query = select(func.count(Appointment.id)).where(
        Appointment.is_deleted == False,
        Appointment.treatment_phase == "巩固期",
    )
    gj_appt_query = apply_doctor_filter(gj_appt_query, current_user, session)
    gj_appt_count = session.exec(gj_appt_query).one() or 0

    gj_patient_query = select(func.count(distinct(Appointment.patient_id))).where(
        Appointment.is_deleted == False,
        Appointment.treatment_phase == "巩固期",
    )
    gj_patient_query = apply_doctor_filter(gj_patient_query, current_user, session)
    gj_patient_count = session.exec(gj_patient_query).one() or 0

    return {
        "强化期": round(qh_count / denominator * 100, 1),
        "巩固期": round(gj_appt_count / gj_patient_count * 100, 1) if gj_patient_count > 0 else 0,
    }


@router.get("/charts/dot-rates")
def get_dot_rates(
    session: Session = Depends(get_session),
    current_user: Optional[User] = Depends(get_optional_user),
):
    denom_query = select(func.count(distinct(Appointment.patient_id))).where(
        Appointment.is_deleted == False
    )
    denom_query = apply_doctor_filter(denom_query, current_user, session)
    denominator = session.exec(denom_query).one() or 0

    if denominator == 0:
        return {"rate4": 0, "rate5": 0, "rate6": 0}

    result = {}
    for n in [4, 5, 6]:
        count_query = select(func.count(distinct(Appointment.patient_id))).where(
            Appointment.is_deleted == False,
            Appointment.status == "completed",
            Appointment.injection_count >= n,
        )
        count_query = apply_doctor_filter(count_query, current_user, session)
        count = session.exec(count_query).one() or 0
        result[f"rate{n}"] = round(count / denominator * 100, 1)

    return result


@router.get("/charts/distribution")
def get_distributions(
    session: Session = Depends(get_session),
    current_user: Optional[User] = Depends(get_optional_user),
):
    # 眼别分布
    patient_query = select(Patient.left_eye, Patient.right_eye).where(Patient.is_deleted == False)
    patient_query = apply_patient_doctor_filter(patient_query, current_user, session)
    patients = session.exec(patient_query).all()

    left_only = sum(1 for l, r in patients if l and not r)
    right_only = sum(1 for l, r in patients if r and not l)
    both = sum(1 for l, r in patients if l and r)

    eyes = []
    if left_only > 0:
        eyes.append({"name": "左眼", "value": left_only})
    if right_only > 0:
        eyes.append({"name": "右眼", "value": right_only})
    if both > 0:
        eyes.append({"name": "双眼", "value": both})

    # 病种分布
    disease_query = select(Patient.diagnosis, func.count(Patient.id)).where(
        Patient.is_deleted == False
    )
    disease_query = apply_patient_doctor_filter(disease_query, current_user, session)
    disease_query = disease_query.group_by(Patient.diagnosis)
    disease_counts = session.exec(disease_query).all()
    diseases = [{"name": r[0] or "未填写", "value": r[1]} for r in disease_counts]

    return {"eyes": eyes, "diseases": diseases}


@router.get("/charts/doctors")
def get_doctor_workload(
    session: Session = Depends(get_session),
    current_user: Optional[User] = Depends(get_optional_user),
):
    # 各医生总预约条数
    total_query = select(Appointment.doctor, func.count(Appointment.id)).where(
        Appointment.is_deleted == False,
    )
    total_query = apply_doctor_filter(total_query, current_user, session)
    total_rows = session.exec(total_query.group_by(Appointment.doctor)).all()

    # 各医生强化期条数
    qh_query = select(Appointment.doctor, func.count(Appointment.id)).where(
        Appointment.is_deleted == False,
        Appointment.treatment_phase == "强化期",
    )
    qh_query = apply_doctor_filter(qh_query, current_user, session)
    qh_rows = session.exec(qh_query.group_by(Appointment.doctor)).all()

    # 各医生巩固期条数
    gj_query = select(Appointment.doctor, func.count(Appointment.id)).where(
        Appointment.is_deleted == False,
        Appointment.treatment_phase == "巩固期",
    )
    gj_query = apply_doctor_filter(gj_query, current_user, session)
    gj_rows = session.exec(gj_query.group_by(Appointment.doctor)).all()

    total_map = {r[0] or "未知": r[1] for r in total_rows}
    qh_map = {r[0] or "未知": r[1] for r in qh_rows}
    gj_map = {r[0] or "未知": r[1] for r in gj_rows}

    result = []
    for doc, total in total_map.items():
        if total == 0:
            continue
        qh_rate = round(qh_map.get(doc, 0) / total * 100, 1)
        gj_rate = round(gj_map.get(doc, 0) / total * 100, 1)
        result.append({"name": doc, "强化期": qh_rate, "巩固期": gj_rate})

    result.sort(key=lambda x: x["强化期"] + x["巩固期"], reverse=True)
    return result[:10]
