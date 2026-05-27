"""医院6适配器 - 湖南医药学院总医院

Oracle 视图：eyes_department_mrs_operation
字段：INPATIENT_NO, RECORD_NO, IN_TIMES, NAME, OUT_TIME, PRESENT_TEL,
      DIAG_CODE, DIAG_NAME, OPERATION_DATE, OPERATION, OPERATION_DRUG
"""
from core.logger import logger


def _get(row, *names):
    """兼容 Oracle 返回的大写列名和少量可能的小写列名。"""
    for name in names:
        if name in row and row.get(name) is not None:
            return row.get(name)
        lower_name = name.lower()
        if lower_name in row and row.get(lower_name) is not None:
            return row.get(lower_name)
    return None


def _str(value):
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def convert_patient(row, his_conn=None):
    """转换湖南医药学院总医院的手术患者数据。"""
    try:
        inpatient_no = _str(_get(row, "INPATIENT_NO"))
        record_no = _str(_get(row, "RECORD_NO"))
        in_times = _str(_get(row, "IN_TIMES"))
        name = _str(_get(row, "NAME", "XM"))
        phone = _str(_get(row, "PRESENT_TEL"))
        diagnosis_code = _str(_get(row, "DIAG_CODE"))
        diagnosis_name = _str(_get(row, "DIAG_NAME"))
        operation_date = _str(_get(row, "OPERATION_DATE"))
        operation = _str(_get(row, "OPERATION"))
        operation_drug = _str(_get(row, "OPERATION_DRUG"))

        if not record_no:
            logger.debug(f"住院号为空，跳过患者: {name}, 住院流水号: {inpatient_no}")
            return None

        if not name:
            logger.warning(f"患者姓名为空，住院号: {record_no}")

        diagnosis_parts = []
        if diagnosis_code:
            diagnosis_parts.append(diagnosis_code)
        if diagnosis_name:
            diagnosis_parts.append(diagnosis_name)
        diagnosis = " ".join(diagnosis_parts) if diagnosis_parts else None

        logger.debug(
            f"转换湖南医药学院总医院患者: {record_no} -> {name}, "
            f"诊断: {diagnosis_name}, 手术: {operation}"
        )

        return {
            "name": name or "",
            "outpatient_number": record_no,
            "medical_card_number": inpatient_no,
            "phone": phone,
            "diagnosis": diagnosis,
            "drug_type": operation_drug,
            "patient_type": "住院",
            "left_eye": None,
            "right_eye": None,
            "injection_count": None,
            "remarks": (
                f"住院次数: {in_times or ''}; "
                f"出院时间: {_str(_get(row, 'OUT_TIME')) or ''}; "
                f"手术日期: {operation_date or ''}; "
                f"手术: {operation or ''}"
            ),
        }

    except Exception as e:
        logger.error(f"转换湖南医药学院总医院患者数据失败: {e}, 原始数据: {dict(row)}")
        return None
