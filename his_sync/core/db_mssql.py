import pyodbc
import yaml
import time
from core.logger import logger


def get_conn(max_retries=3, retry_delay=5):
    """
    获取 SQL Server 连接，支持重试机制 (使用 pyodbc)
    """
    with open("config/config.yaml") as f:
        cfg = yaml.safe_load(f)

    his = cfg["his"]
    
    for attempt in range(max_retries):
        try:
            logger.debug(f"尝试连接 SQL Server (第 {attempt + 1} 次)")
            
            # 获取可用的 SQL Server 驱动
            drivers = pyodbc.drivers()
            sql_drivers = [d for d in drivers if 'SQL Server' in d]
            
            if not sql_drivers:
                raise Exception("未找到 SQL Server ODBC 驱动")
            
            driver = sql_drivers[0]  # 使用第一个可用驱动
            logger.debug(f"使用 ODBC 驱动: {driver}")
            
            # 构建连接字符串
            conn_str = f"""
                DRIVER={{{driver}}};
                SERVER={his['host']},{his['port']};
                DATABASE={his['db']};
                UID={his['user']};
                PWD={his['password']};
                Timeout=30;
                LoginTimeout=30;
            """
            
            conn = pyodbc.connect(conn_str)
            logger.debug("SQL Server 连接成功")
            return conn
            
        except Exception as e:
            logger.warning(f"SQL Server 连接失败 (第 {attempt + 1} 次): {e}")
            if attempt < max_retries - 1:
                logger.info(f"等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
            else:
                logger.error("SQL Server 连接失败，已达到最大重试次数")
                raise