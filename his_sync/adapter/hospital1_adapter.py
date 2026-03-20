from core.logger import logger


def convert_patient(row):
    """
    转换第一家医院的患者数据
    字段映射：
    BRXM -> name (病人姓名)
    ZYH -> outpatient_number (住院号)
    ZJHM -> medical_card_number (证件号码作为就诊卡号)
    """
    try:
        # 数据转换和验证
        name = str(row["BRXM"]) if row.get("BRXM") is not None else ""
        outpatient_number = str(row["ZYH"]) if row.get("ZYH") is not None else None
        medical_card_number = str(row["ZJHM"]) if row.get("ZJHM") is not None else None
        
        # 第一家医院的视图没有这些字段，设为 None
        phone = None
        diagnosis = None
        patient_type = None
        
        # 数据验证
        if not name or not name.strip():
            logger.warning(f"患者姓名为空，住院号: {outpatient_number}")
            
        result = {
            "name": name.strip() if name else "",
            "outpatient_number": outpatient_number,
            "medical_card_number": medical_card_number,
            "phone": phone,
            "diagnosis": diagnosis,
            "patient_type": patient_type
        }
        
        logger.debug(f"转换第一家医院患者数据: {outpatient_number} -> {name}")
        return result
        
    except Exception as e:
        logger.error(f"转换第一家医院患者数据失败: {e}, 原始数据: {dict(row)}")
        # 返回默认值以避免同步中断
        return {
            "name": "数据转换错误",
            "outpatient_number": None,
            "medical_card_number": None,
            "phone": None,
            "diagnosis": None,
            "patient_type": None
        }