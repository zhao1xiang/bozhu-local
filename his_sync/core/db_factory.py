"""
数据库连接工厂，支持多医院连接
"""
import pyodbc
import time
from core.logger import logger


def get_his_conn(hospital_config, max_retries=3, retry_delay=5):
    """
    根据医院配置获取 HIS 数据库连接
    """
    his_config = hospital_config["his"]
    hospital_name = hospital_config["name"]
    
    for attempt in range(max_retries):
        try:
            logger.debug(f"尝试连接 {hospital_name} HIS 数据库 (第 {attempt + 1} 次)")
            
            # 构建连接字符串
            server = f"{his_config['host']},{his_config['port']}"
            database = his_config["db"]
            username = his_config["user"]
            password = his_config["password"]
            
            # 优先使用配置中指定的编码
            preferred_charset = his_config.get("charset", "cp936")
            
            # 根据编码设置不同的连接字符串
            if preferred_charset in ["utf8", "utf-8"]:
                conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};CHARSET=UTF8;"
            else:
                conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};"
            
            try:
                conn = pyodbc.connect(conn_str, timeout=30)
                
                # 测试查询以验证编码是否正确
                cursor = conn.cursor()
                
                # 根据不同医院使用不同的测试查询
                if hospital_config.get("id") == "hospital2":
                    # hospital2 使用 patient_source 表
                    cursor.execute("SELECT TOP 1 name FROM patient_source WHERE name IS NOT NULL AND name != ''")
                else:
                    # hospital1 使用 VW_VEGF_PATIENT 视图
                    cursor.execute("SELECT TOP 1 BRXM as name FROM VW_VEGF_PATIENT WHERE BRXM IS NOT NULL AND BRXM != ''")
                
                test_row = cursor.fetchone()
                cursor.close()
                
                if test_row and test_row[0] and test_row[0].strip():
                    # 检查是否包含中文字符且没有乱码
                    test_name = test_row[0]
                    if len(test_name) > 0 and not any(ord(c) > 127 and c in 'ÀîËÄÍõÎåÕÅÈý' for c in test_name):
                        logger.info(f"{hospital_name} HIS 数据库连接成功，使用编码: {preferred_charset}")
                        logger.debug(f"测试数据: {repr(test_name)}")
                        return conn
                
                conn.close()
                        
            except Exception as e:
                logger.debug(f"编码 {preferred_charset} 连接失败: {e}")
                
                # 如果首选编码失败，尝试其他编码
                other_charsets = ["cp936", "utf8"] if preferred_charset != "cp936" else ["utf8"]
                
                for charset in other_charsets:
                    try:
                        if charset in ["utf8", "utf-8"]:
                            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};CHARSET=UTF8;"
                        else:
                            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};"
                        
                        conn = pyodbc.connect(conn_str, timeout=30)
                        
                        # 测试查询
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
            
            # 如果所有编码都失败，使用默认连接
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};"
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