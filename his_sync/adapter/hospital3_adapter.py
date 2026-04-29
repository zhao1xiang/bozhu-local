"""
医院3适配器 - WebService 接口（智业集成平台）
将 GetResiVisitRecord 返回的住院信息转换为我们的患者格式
"""
from core.logger import logger

# 诊断白名单（眼科相关）
VALID_DIAGNOSES = {
    "视网膜静脉阻塞", "糖尿病性视网膜病变", "脉络膜新生血管", "黄斑变性",
    "老年性黄斑变性", "糖尿病视网膜病", "黄斑水肿", "视网膜分支静脉阻塞",
    "视网膜中心性静脉阻塞", "玻璃体积血", "眼底出血", "虹膜新生血管",
    "nAMD", "DME", "RVO", "AMD", "CNV", "mCNV", "PCV",
}


def convert_patient(row: dict):
    """
    将 GetResiVisitRecord 返回的一条住院记录转换为患者字典
    row 字段来自 XML 解析结果
    """
    try:
        visit_no = str(row.get("visitNo", "")).strip()          # 住院号 -> outpatient_number
        patient_id = str(row.get("patientId", "")).strip()      # 病人ID -> medical_card_number
        name = str(row.get("patientName", "")).strip()
        diagnosis = str(row.get("inDiagnosisName", "")).strip()
        dept_name = str(row.get("nursingDeptName", "")).strip() or str(row.get("inDeptName", "")).strip()

        if not visit_no:
            logger.debug(f"住院号为空，跳过: {name}")
            return None

        if not name:
            logger.warning(f"患者姓名为空，住院号: {visit_no}")

        # 诊断白名单过滤（可选，注释掉则同步所有）
        # if diagnosis and not any(d in diagnosis for d in VALID_DIAGNOSES):
        #     logger.debug(f"诊断 '{diagnosis}' 不在白名单，跳过: {visit_no}")
        #     return None

        logger.debug(f"转换患者: {visit_no} -> {name}, 诊断: {diagnosis}, 科室: {dept_name}")

        return {
            "name": name,
            "outpatient_number": visit_no,
            "medical_card_number": patient_id or None,
            "phone": None,          # 该接口不返回手机号
            "diagnosis": diagnosis or None,
            "patient_type": None,   # 该接口不返回患者类型
            "left_eye": False,
            "right_eye": False,
            "injection_count": None,
            "dept_name": dept_name, # 科室名，可用于病区匹配（暂存，upsert 时忽略）
        }

    except Exception as e:
        logger.error(f"转换住院患者数据失败: {e}, 原始数据: {row}")
        return None
