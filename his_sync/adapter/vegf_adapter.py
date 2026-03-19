from core.logger import logger


def convert_patient(row):
    """
    转换患者数据，将SQL Server视图字段映射到SQLite表字段
    ZYH -> outpatient_number
    BRXM -> name (修正字段映射)
    """
    try:
        # 调试：打印所有可用字段
        if hasattr(row, 'cursor_description'):
            available_fields = [desc[0] for desc in row.cursor_description]
            logger.debug(f"可用字段: {available_fields}")
        
        # 尝试不同的字段名（大小写）
        outpatient_number = None
        name = ""
        
        # 查找门诊号字段
        for field_name in ['ZYH', 'zyh', 'Zyh']:
            try:
                if hasattr(row, field_name) or field_name in row:
                    value = getattr(row, field_name, None) or row[field_name]
                    if value is not None:
                        outpatient_number = str(value)
                        break
            except:
                continue
        
        # 查找姓名字段
        for field_name in ['BRXM', 'brxm', 'Brxm']:
            try:
                if hasattr(row, field_name) or field_name in row:
                    value = getattr(row, field_name, None) or row[field_name]
                    if value is not None:
                        name = str(value)
                        break
            except:
                continue
        
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
        logger.error(f"转换患者数据失败: {e}")
        # 返回默认值以避免同步中断
        return {
            "outpatient_number": None,
            "name": "数据转换错误"
        }