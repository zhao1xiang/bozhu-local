"""
医院5适配器 - 潍坊眼科医院
视图字段与医院4相同：name, outpatient_number, medical_card_number, phone,
          diagnosis, drug_name, eye, injection_count,
          left_vision, right_vision, left_vision_corrected, right_vision_corrected,
          blood_pressure, blood_sugar, doctor
"""
from core.logger import logger

VALID_DIAGNOSES = {
    "视网膜静脉阻塞", "糖尿病性视网膜病变", "脉络膜新生血管", "黄斑变性",
    "老年性黄斑变性", "糖尿病视网膜病", "黄斑水肿", "视网膜分支静脉阻塞",
    "视网膜中心性静脉阻塞", "玻璃体积血", "眼底出血", "虹膜新生血管",
    "nAMD", "DME", "RVO", "AMD", "CNV", "mCNV", "PCV",
}


def _str(val):
    """安全转字符串，None 返回 None"""
    if val is None:
        return None
    s = str(val).strip()
    return s if s else None


def convert_patient(row):
    """
    转换山东第一医科大学附属青岛眼科医院的患者数据
    """
    try:
        name               = _str(row.get("name"))
        outpatient_number  = _str(row.get("outpatient_number"))
        medical_card_number = _str(row.get("medical_card_number"))
        phone              = _str(row.get("phone"))
        diagnosis          = _str(row.get("diagnosis"))
        drug_name          = _str(row.get("drug_name"))
        eye_raw            = _str(row.get("eye")) or ""
        doctor             = _str(row.get("doctor"))

        # 视力字段
        left_vision              = _str(row.get("left_vision"))
        right_vision             = _str(row.get("right_vision"))
        left_vision_corrected    = _str(row.get("left_vision_corrected"))
        right_vision_corrected   = _str(row.get("right_vision_corrected"))

        # 血压血糖（暂存备用，upsert 时不写入患者表，可扩展）
        # blood_pressure = _str(row.get("blood_pressure"))
        # blood_sugar    = _str(row.get("blood_sugar"))

        # 诊断白名单过滤
        #if diagnosis and diagnosis not in VALID_DIAGNOSES:
        #    logger.debug(f"诊断 '{diagnosis}' 不在白名单，跳过患者: {outpatient_number}")
        #    return None

        if not outpatient_number:
            logger.debug(f"住院号为空，跳过: {name}")
            return None

        if not name:
            logger.warning(f"患者姓名为空，住院号: {outpatient_number}")

        # 眼别转换
        left_eye  = eye_raw in ["左眼", "双眼"]
        right_eye = eye_raw in ["右眼", "双眼"]

        # 已完成针数
        try:
            injection_count = int(row["injection_count"]) if row.get("injection_count") is not None else None
        except (ValueError, TypeError):
            injection_count = None

        logger.debug(f"转换患者: {outpatient_number} -> {name}, 诊断: {diagnosis}, 药物: {drug_name}")

        return {
            "name":                    name or "",
            "outpatient_number":       outpatient_number,
            "medical_card_number":     medical_card_number,
            "phone":                   phone,
            "diagnosis":               diagnosis,
            "drug_type":               drug_name,       # 视图字段 drug_name -> 我们的 drug_type
            "patient_type":            None,            # 视图未提供
            "left_eye":                left_eye,
            "right_eye":               right_eye,
            "injection_count":         injection_count,
            "left_vision":             left_vision,
            "right_vision":            right_vision,
            "left_vision_corrected":   left_vision_corrected,
            "right_vision_corrected":  right_vision_corrected,
            "doctor":                  doctor,
        }

    except Exception as e:
        logger.error(f"转换潍坊眼科医院患者数据失败: {e}, 原始数据: {dict(row)}")
        return None
