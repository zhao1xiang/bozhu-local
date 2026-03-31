from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func, distinct
from database import engine
from models import Appointment, Patient, FollowUpRecord
from datetime import date, timedelta
import collections

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def get_session():
    with Session(engine) as session:
        yield session


@router.get("/stats")
def get_dashboard_stats(session: Session = Depends(get_session)):
    today = date.today()

    # 累计患者数
    total_patients = session.exec(
        select(func.count(Patient.id)).where(Patient.is_deleted == False)
    ).one()

    # 累计完成注药
    total_injections = session.exec(
        select(func.count(Appointment.id)).where(
            Appointment.status == 'completed',
            Appointment.is_deleted == False
        )
    ).one()

    # 今日预约
    today_appointments = session.exec(
        select(func.count(Appointment.id)).where(
            Appointment.appointment_date == today,
            Appointment.is_deleted == False
        )
    ).one()

    # 复诊提醒（今日到期）
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
    today = date.today()
    start_date = today - timedelta(days=180)

    appointments = session.exec(
        select(Appointment).where(
            Appointment.is_deleted == False,
            Appointment.appointment_date >= start_date,
            Appointment.status == 'completed'
        ).order_by(Appointment.appointment_date)
    ).all()

    counts = collections.defaultdict(int)
    for appt in appointments:
        if dimension == "week":
            key = appt.appointment_date.strftime("%Y-W%W")
        else:
            key = appt.appointment_date.strftime("%Y-%m")
        counts[key] += 1

    return [{"date": k, "count": v} for k, v in sorted(counts.items())]


@router.get("/charts/reinjection-rate")
def get_reinjection_rate(session: Session = Depends(get_session)):
    """
    强化期约针率 = 强化期预约条数总和 / 有过预约的建档患者数
    巩固期约针率 = 巩固期内有过预约的患者数 / 有过预约的建档患者数
    """
    # 分母：有过预约的建档患者数
    denominator = session.exec(
        select(func.count(distinct(Appointment.patient_id))).where(
            Appointment.is_deleted == False
        )
    ).one() or 0

    if denominator == 0:
        return {"强化期": 0, "巩固期": 0}

    # 强化期：条数
    qh_count = session.exec(
        select(func.count(Appointment.id)).where(
            Appointment.is_deleted == False,
            Appointment.treatment_phase == "强化期",
        )
    ).one() or 0

    # 巩固期：条数 / 巩固期去重患者数
    gj_appt_count = session.exec(
        select(func.count(Appointment.id)).where(
            Appointment.is_deleted == False,
            Appointment.treatment_phase == "巩固期",
        )
    ).one() or 0

    gj_patient_count = session.exec(
        select(func.count(distinct(Appointment.patient_id))).where(
            Appointment.is_deleted == False,
            Appointment.treatment_phase == "巩固期",
        )
    ).one() or 0

    return {
        "强化期": round(qh_count / denominator * 100, 1),
        "巩固期": round(gj_appt_count / gj_patient_count * 100, 1) if gj_patient_count > 0 else 0,
    }


@router.get("/charts/dot-rates")
def get_dot_rates(session: Session = Depends(get_session)):
    """
    4针率 = 完成预约中 injection_count >= 4 的患者数 / 有过预约的建档患者数
    5针率 = 完成预约中 injection_count >= 5 的患者数 / 有过预约的建档患者数
    6针率 = 完成预约中 injection_count >= 6 的患者数 / 有过预约的建档患者数
    """
    denominator = session.exec(
        select(func.count(distinct(Appointment.patient_id))).where(
            Appointment.is_deleted == False
        )
    ).one() or 0

    if denominator == 0:
        return {"rate4": 0, "rate5": 0, "rate6": 0}

    result = {}
    for n in [4, 5, 6]:
        count = session.exec(
            select(func.count(distinct(Appointment.patient_id))).where(
                Appointment.is_deleted == False,
                Appointment.status == "completed",
                Appointment.injection_count >= n,
            )
        ).one() or 0
        result[f"rate{n}"] = round(count / denominator * 100, 1)

    return result


@router.get("/charts/distribution")
def get_distributions(session: Session = Depends(get_session)):
    # 眼别分布（按患者表的 left_eye / right_eye 字段统计）
    patients = session.exec(
        select(Patient.left_eye, Patient.right_eye).where(Patient.is_deleted == False)
    ).all()

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

    # 病种分布（按患者诊断）
    disease_query = select(Patient.diagnosis, func.count(Patient.id)).where(
        Patient.is_deleted == False
    ).group_by(Patient.diagnosis)
    disease_counts = session.exec(disease_query).all()
    diseases = [{"name": r[0] or "未填写", "value": r[1]} for r in disease_counts]

    return {"eyes": eyes, "diseases": diseases}


@router.get("/charts/doctors")
def get_doctor_workload(session: Session = Depends(get_session)):
    """
    医生约针率排行 Top 10
    强化期率 = 该医生强化期预约条数 / 该医生总预约条数
    巩固期率 = 该医生巩固期预约条数 / 该医生总预约条数
    """
    # 各医生总预约条数
    total_rows = session.exec(
        select(Appointment.doctor, func.count(Appointment.id)).where(
            Appointment.is_deleted == False,
        ).group_by(Appointment.doctor)
    ).all()

    # 各医生强化期条数
    qh_rows = session.exec(
        select(Appointment.doctor, func.count(Appointment.id)).where(
            Appointment.is_deleted == False,
            Appointment.treatment_phase == "强化期",
        ).group_by(Appointment.doctor)
    ).all()

    # 各医生巩固期条数
    gj_rows = session.exec(
        select(Appointment.doctor, func.count(Appointment.id)).where(
            Appointment.is_deleted == False,
            Appointment.treatment_phase == "巩固期",
        ).group_by(Appointment.doctor)
    ).all()

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
