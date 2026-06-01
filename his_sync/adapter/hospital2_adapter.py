from core.logger import logger

VALID_DIAGNOSES = {
    "视网膜静脉阻塞", "糖尿病性视网膜病变", "脉络膜新生血管", "黄斑变性",
    "老年性黄斑变性", "糖尿病视网膜病", "黄斑水肿", "视网膜分支静脉阻塞",
    "视网膜中心性静脉阻塞", "玻璃体积血", "眼底出血", "虹膜新生血管"
}


def _get(row, name):
    if name in row:
        return row.get(name)

    for key, value in row.items():
        if str(key).strip().lower() == name.lower():
            return value
    return None


def _str(value):
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def convert_patient(row):
    """
    转换第二家医院的患者数据
    """
    try:
        name = _str(_get(row, "name"))
        outpatient_number = _str(_get(row, "outpatient_number"))
        medical_card_number = _str(_get(row, "medical_card_number"))
        phone = _str(_get(row, "phone"))
        diagnosis = _str(_get(row, "diagnosis"))
        drug_name = _str(_get(row, "drug_name"))
        patient_type = _str(_get(row, "patient_type"))
        
        # 诊断白名单过滤，不在列表内直接跳过
        if diagnosis not in VALID_DIAGNOSES:
            logger.debug(f"诊断 '{diagnosis}' 不在白名单，跳过患者: {outpatient_number}")
            return None
        
        # 眼别转换：左眼/右眼/双眼 -> left_eye/right_eye bool
        eye_raw = _str(_get(row, "eye")) or ""
        left_eye = eye_raw in ["左眼", "双眼"]
        right_eye = eye_raw in ["右眼", "双眼"]

        # 已完成针数
        injection_count_raw = _get(row, "injection_count")
        injection_count = int(injection_count_raw) if injection_count_raw is not None else None

        if not name:
            logger.warning(f"患者姓名为空，住院号: {outpatient_number}")

        logger.debug(f"转换患者: {outpatient_number} -> {name}, 诊断: {diagnosis}")
        return {
            "name": name or "",
            "outpatient_number": outpatient_number,
            "medical_card_number": medical_card_number,
            "phone": phone,
            "diagnosis": diagnosis,
            "drug_type": drug_name,
            "patient_type": patient_type,
            "left_eye": left_eye,
            "right_eye": right_eye,
            "injection_count": injection_count,
        }

    except Exception as e:
        logger.error(f"转换第二家医院患者数据失败: {e}, 原始数据: {dict(row)}")
        return None
