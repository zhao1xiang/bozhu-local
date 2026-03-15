from core.logger import logger


def convert_patient(row):
    """
    转换患者数据，将SQL Server视图字段映射到SQLite表字段
    ZYH -> outpatient_number
    BRXM -> name (修正字段映射)
    """
    try:
        outpatient_number = str(row["ZYH"]) if row.get("ZYH") is not None else None
        name = str(row["BRXM"]) if row.get("BRXM") is not None else ""
        
        # 数据验证
        if not name.strip():
            logger.warning(f"患者姓名为空，门诊号: {outpatient_number}")
            
        result = {
            "outpatient_number": outpatient_number,
            "name": name.strip()
        }
        
        logger.debug(f"转换患者数据: {outpatient_number} -> {name}")
        return result
        
    except Exception as e:
        logger.error(f"转换患者数据失败: {e}, 原始数据: {dict(row)}")
        # 返回默认值以避免同步中断
        return {
            "outpatient_number": None,
            "name": "数据转换错误"
        }