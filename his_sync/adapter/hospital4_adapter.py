"""
医院4适配器 - 山东第一医科大学附属青岛眼科医院
视图字段：name, outpatient_number, medical_card_number, phone,
          diagnosis, drug_name, eye, injection_count,
          left_vision, right_vision, left_vision_corrected, right_vision_corrected,
          blood_pressure, blood_sugar, doctor, bz, yyrq, ryrq
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


def _get(row, *names):
    """Get a value from a DB row using case/space-insensitive column names."""
    for name in names:
        if name in row:
            return row.get(name)

    normalized = {str(key).strip().lower(): value for key, value in row.items()}
    for name in names:
        value = normalized.get(str(name).strip().lower())
        if value is not None:
            return value
    return None


def convert_patient(row):
    """
    转换山东第一医科大学附属青岛眼科医院的患者数据
    """
    try:
        name               = _str(_get(row, "name"))
        outpatient_number  = _str(_get(row, "outpatient_number"))
        medical_card_number = _str(_get(row, "medical_card_number"))
        phone              = _str(_get(row, "phone"))
        diagnosis          = _str(_get(row, "diagnosis"))
        drug_name          = _str(_get(row, "drug_name"))
        eye_raw            = _str(_get(row, "eye")) or ""
        doctor             = _str(_get(row, "doctor"))
        remarks            = _str(_get(row, "bz"))
        yyrq               = _str(_get(row, "yyrq"))
        ryrq               = _str(_get(row, "ryrq"))

        # 视力字段
        left_vision              = _str(_get(row, "left_vision"))
        right_vision             = _str(_get(row, "right_vision"))
        left_vision_corrected    = _str(_get(row, "left_vision_corrected"))
        right_vision_corrected   = _str(_get(row, "right_vision_corrected"))

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

        # 眼别转换，兼容医院视图只传“左/右/双”的情况
        normalized_eye = eye_raw.replace(" ", "").replace("　", "")
        left_eye = normalized_eye in ["左", "左眼", "双", "双眼", "双侧", "两眼"]
        right_eye = normalized_eye in ["右", "右眼", "双", "双眼", "双侧", "两眼"]

        # 已完成针数
        try:
            injection_count_raw = _get(row, "injection_count")
            injection_count = int(injection_count_raw) if injection_count_raw is not None else None
        except (ValueError, TypeError):
            injection_count = None

        logger.debug(f"转换患者: {outpatient_number} -> {name}, 诊断: {diagnosis}, 药物: {drug_name}")

        logger.info(f"hospital4 date fields: outpatient_number={outpatient_number}, yyrq={yyrq}, ryrq={ryrq}")

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
            "remarks":                 remarks,
            "yyrq":                    yyrq,
            "ryrq":                    ryrq,
        }

    except Exception as e:
        logger.error(f"转换青岛眼科医院患者数据失败: {e}, 原始数据: {dict(row)}")
        return None
