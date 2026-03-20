"""
数据库连接工厂，支持多医院连接
"""
import pyodbc
import time
from core.logger import logger


# SQL Server ODBC 驱动优先级列表（从新到旧）
MSSQL_DRIVERS = [
    "ODBC Driver 18 for SQL Server",
    "ODBC Driver 17 for SQL Server",
    "ODBC Driver 13 for SQL Server",
    "ODBC Driver 11 for SQL Server",
    "SQL Server Native Client 11.0",
    "SQL Server Native Client 10.0",
    "SQL Server",
]


def get_available_driver():
    """获取系统中可用的 SQL Server ODBC 驱动"""
    installed = pyodbc.drivers()
    for driver in MSSQL_DRIVERS:
        if driver in installed:
            logger.info(f"使用 ODBC 驱动: {driver}")
            return driver
    logger.error(f"未找到可用的 SQL Server ODBC 驱动，已安装驱动: {installed}")
    raise RuntimeError(f"未找到 SQL Server ODBC 驱动，请安装 ODBC Driver for SQL Server")


def get_his_conn(hospital_config, max_retries=3, retry_delay=5):
    """
    根据医院配置获取 HIS 数据库连接
    """
    his_config = hospital_config["his"]
    hospital_name = hospital_config["name"]
    
    # 获取可用驱动（只检测一次）
    try:
        driver = get_available_driver()
    except RuntimeError as e:
        raise

    for attempt in range(max_retries):
        try:
            logger.debug(f"尝试连接 {hospital_name} HIS 数据库 (第 {attempt + 1} 次)")
            
            server = f"{his_config['host']},{his_config['port']}"
            database = his_config["db"]
            username = his_config["user"]
            password = his_config["password"]
            preferred_charset = his_config.get("charset", "cp936")
            
            if preferred_charset in ["utf8", "utf-8"]:
                conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password};CHARSET=UTF8;"
            else:
                conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password};"
            
            try:
                conn = pyodbc.connect(conn_str, timeout=30)
                
                cursor = conn.cursor()
                if hospital_config.get("id") == "hospital2":
                    cursor.execute("SELECT TOP 1 name FROM patient_source WHERE name IS NOT NULL AND name != ''")
                else:
                    cursor.execute("SELECT TOP 1 BRXM as name FROM VW_VEGF_PATIENT WHERE BRXM IS NOT NULL AND BRXM != ''")
                
                test_row = cursor.fetchone()
                cursor.close()
                
                if test_row and test_row[0] and test_row[0].strip():
                    test_name = test_row[0]
                    if len(test_name) > 0 and not any(ord(c) > 127 and c in 'ÀîËÄÍõÎåÕÅÈý' for c in test_name):
                        logger.info(f"{hospital_name} HIS 数据库连接成功，使用编码: {preferred_charset}")
                        logger.debug(f"测试数据: {repr(test_name)}")
                        return conn
                
                conn.close()
                        
            except Exception as e:
                logger.debug(f"编码 {preferred_charset} 连接失败: {e}")
                
                other_charsets = ["cp936", "utf8"] if preferred_charset != "cp936" else ["utf8"]
                
                for charset in other_charsets:
                    try:
                        if charset in ["utf8", "utf-8"]:
                            conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password};CHARSET=UTF8;"
                        else:
                            conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password};"
                        
                        conn = pyodbc.connect(conn_str, timeout=30)
                        cursor = conn.cursor()
                        if hospital_config.get("id") == "hospital2":
                            cursor.execute("SELECT TOP 1 name FROM patient_source WHERE name IS NOT NULL AND name != ''")
                        else:
                            cursor.execute("SELECT TOP 1 BRXM as name FROM VW_VEGF_PATIENT WHERE BRXM IS NOT NULL AND BRXM != ''")
                        
                        test_row = cursor.fetchone()
                        cursor.close()
                        
                        if test_row and test_row[0] and test_row[0].strip():
                            test_name = test_row[0]
                            if len(test_name) > 0 and not any(ord(c) > 127 and c in 'ÀîËÄÍõÎåÕÅÈý' for c in test_name):
                                logger.info(f"{hospital_name} HIS 数据库连接成功，使用编码: {charset}")
                                logger.debug(f"测试数据: {repr(test_name)}")
                                return conn
                        
                        conn.close()
                        
                    except Exception as e2:
                        logger.debug(f"编码 {charset} 连接失败: {e2}")
                        continue
            
            # 所有编码都失败，使用默认连接
            conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password};"
            conn = pyodbc.connect(conn_str, timeout=30)
            logger.warning(f"{hospital_name} HIS 数据库连接成功，但可能存在编码问题")
            return conn
            
        except Exception as e:
            logger.warning(f"{hospital_name} HIS 数据库连接失败 (第 {attempt + 1} 次): {e}")
            if attempt < max_retries - 1:
                logger.info(f"等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
            else:
                logger.error(f"{hospital_name} HIS 数据库连接失败，已达到最大重试次数")
                raise


def get_adapter(adapter_name):
    """
    动态加载适配器模块
    """
    try:
        if adapter_name == "hospital1_adapter":
            from adapter.hospital1_adapter import convert_patient
        elif adapter_name == "hospital2_adapter":
            from adapter.hospital2_adapter import convert_patient
        else:
            raise ValueError(f"未知的适配器: {adapter_name}")
        
        logger.debug(f"成功加载适配器: {adapter_name}")
        return convert_patient
        
    except Exception as e:
        logger.error(f"加载适配器失败: {adapter_name}, 错误: {e}")
        raise