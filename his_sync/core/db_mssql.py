import pymssql
import yaml
import time
from core.logger import logger


def get_conn(max_retries=3, retry_delay=5):
    """
    获取 SQL Server 连接，支持重试机制
    """
    with open("config/config.yaml") as f:
        cfg = yaml.safe_load(f)

    his = cfg["his"]
    
    for attempt in range(max_retries):
        try:
            logger.debug(f"尝试连接 SQL Server (第 {attempt + 1} 次)")
            conn = pymssql.connect(
                host=str(his["host"]),
                port=str(his["port"]),
                user=str(his["user"]),
                password=str(his["password"]),
                database=str(his["db"]),
                charset='cp936',
                timeout=30,  # 连接超时
                login_timeout=30  # 登录超时
            )
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