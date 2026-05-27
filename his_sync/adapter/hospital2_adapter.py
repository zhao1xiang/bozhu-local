from core.logger import logger

VALID_DIAGNOSES = {
    "视网膜静脉阻塞", "糖尿病性视网膜病变", "脉络膜新生血管", "黄斑变性",
    "老年性黄斑变性", "糖尿病视网膜病", "黄斑水肿", "视网膜分支静脉阻塞",
    "视网膜中心性静脉阻塞", "玻璃体积血", "眼底出血", "虹膜新生血管"
}


def convert_patient(row):
    """
    转换第二家医院的患者数据
    """
    try:
        name = str(row["name"]).strip() if row.get("name") is not None else None
        outpatient_number = str(row["outpatient_number"]) if row.get("outpatient_number") is not None else None
        medical_card_number = str(row["medical_card_number"]) if row.get("medical_card_number") is not None else None
        phone = str(row["phone"]) if row.get("phone") is not None else None
        diagnosis = str(row["diagnosis"]).strip() if row.get("diagnosis") is not None else None
        drug_name = str(row["drug_name"]).strip() if row.get("drug_name") is not None else None
        patient_type = str(row["patient_type"]) if row.get("patient_type") is not None else None
        
        # 诊断白名单过滤，不在列表内直接跳过
        if diagnosis not in VALID_DIAGNOSES:
            logger.debug(f"诊断 '{diagnosis}' 不在白名单，跳过患者: {outpatient_number}")
            return None
        
        # 眼别转换：左眼/右眼/双眼 -> left_eye/right_eye bool
        eye_raw = str(row["eye"]).strip() if row.get("eye") is not None else ""
        left_eye = eye_raw in ["左眼", "双眼"]
        right_eye = eye_raw in ["右眼", "双眼"]

        # 已完成针数
        injection_count = int(row["injection_count"]) if row.get("injection_count") is not None else None

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
