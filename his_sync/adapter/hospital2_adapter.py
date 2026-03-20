from core.logger import logger


def convert_patient(row):
    """
    转换第二家医院的患者数据
    """
    try:
        # 数据转换和验证
        name = str(row["name"]) if row.get("name") is not None else None
        outpatient_number = str(row["outpatient_number"]) if row.get("outpatient_number") is not None else None
        medical_card_number = str(row["medical_card_number"]) if row.get("medical_card_number") is not None else None
        phone = str(row["phone"]) if row.get("phone") is not None else None 
        diagnosis = str(row["diagnosis"]) if row.get("diagnosis") is not None else None  # 医嘱名称作为诊断
        patient_type = str(row["patient_type"]) if row.get("patient_type") is not None else None  # 医嘱权限作为患者类型
        
        # 数据验证
        if not name.strip():
            logger.warning(f"患者姓名为空，住院号: {outpatient_number}")
            
        result = {
            "name": name.strip(),
            "outpatient_number": outpatient_number,
            "medical_card_number": medical_card_number,
            "phone": phone,
            "diagnosis": diagnosis,
            "patient_type": patient_type
        }
        
        logger.debug(f"转换第二家医院患者数据: {outpatient_number} -> {name}, 诊断: {diagnosis}, 类型: {patient_type}")
        return result
        
    except Exception as e:
        logger.error(f"转换第二家医院患者数据失败: {e}, 原始数据: {dict(row)}")
        # 返回默认值以避免同步中断
        return {
            "name": "数据转换错误",
            "outpatient_number": None,
            "medical_card_number": None,
            "phone": None,
            "diagnosis": None,
            "patient_type": None
        }