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
    raise RuntimeError("未找到 SQL Server ODBC 驱动，请安装 ODBC Driver for SQL Server")


def _try_connect(driver, host, port, database, username, password, charset=None):
    """
    依次尝试多种连接格式，兼容新旧驱动
    新驱动支持 host,port；旧驱动（SQL Server）需要 host;PORT=port 格式
    """
    charset_part = ";CHARSET=UTF8" if charset in ["utf8", "utf-8"] else ""
    conn_strs = [
        f"DRIVER={{{driver}}};SERVER={host},{port};DATABASE={database};UID={username};PWD={password}{charset_part};Timeout=30;",
        f"DRIVER={{{driver}}};SERVER={host};PORT={port};DATABASE={database};UID={username};PWD={password}{charset_part};Timeout=30;",
        f"DRIVER={{{driver}}};SERVER=tcp:{host},{port};DATABASE={database};UID={username};PWD={password}{charset_part};Timeout=30;",
        # 旧版 SQL Server 驱动（DBNETLIB）只认不带端口的 host，默认连 1433
        f"DRIVER={{{driver}}};SERVER={host};DATABASE={database};UID={username};PWD={password}{charset_part};Timeout=30;",
    ]
    last_err = None
    for conn_str in conn_strs:
        try:
            conn = pyodbc.connect(conn_str, timeout=30)
            return conn
        except Exception as e:
            last_err = e
    raise last_err


def get_his_conn(hospital_config, max_retries=3, retry_delay=5):
    """根据医院配置获取 HIS 数据库连接"""
    his_config = hospital_config["his"]
    hospital_name = hospital_config["name"]
    host = his_config["host"]
    port = his_config.get("port", 1433)
    database = his_config["db"]
    username = his_config["user"]
    password = his_config["password"]
    preferred_charset = his_config.get("charset", "cp936")

    driver = get_available_driver()

    for attempt in range(max_retries):
        try:
            logger.debug(f"尝试连接 {hospital_name} HIS 数据库 (第 {attempt + 1} 次)")

            # 先用首选编码尝试
            try:
                conn = _try_connect(driver, host, port, database, username, password, preferred_charset)
                logger.info(f"{hospital_name} HIS 数据库连接成功")
                return conn
            except Exception as e:
                logger.debug(f"首选编码 {preferred_charset} 连接失败: {e}")

            # 再用无编码参数尝试
            conn = _try_connect(driver, host, port, database, username, password)
            logger.warning(f"{hospital_name} HIS 数据库连接成功（默认编码）")
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
    """动态加载适配器模块"""
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
