"""
健康检查模块
"""
import yaml
import os
from core.db_mssql import get_conn as his_conn
from core.db_sqlite import get_conn as local_conn
from core.logger import logger


def validate_config():
    """验证配置文件"""
    try:
        with open("config/config.yaml") as f:
            cfg = yaml.safe_load(f)
        
        # 检查必需的配置项
        required_keys = {
            "his": ["host", "port", "user", "password", "db"],
            "sqlite": ["path"],
            "view": ["patient"],
            "sync": ["interval"]
        }
        
        for section, keys in required_keys.items():
            if section not in cfg:
                raise ValueError(f"配置文件缺少 {section} 部分")
            
            for key in keys:
                if key not in cfg[section]:
                    raise ValueError(f"配置文件 {section} 部分缺少 {key} 配置")
        
        # 验证同步间隔
        if cfg["sync"]["interval"] < 60:
            logger.warning("同步间隔小于60秒，可能会对数据库造成压力")
        
        logger.info("配置文件验证通过")
        return True
        
    except Exception as e:
        logger.error(f"配置文件验证失败: {e}")
        return False


def check_database_connections():
    """检查数据库连接"""
    results = {"his": False, "sqlite": False}
    
    # 检查 SQL Server 连接
    try:
        conn = his_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        results["his"] = True
        logger.info("SQL Server 连接检查通过")
    except Exception as e:
        logger.error(f"SQL Server 连接检查失败: {e}")
    
    # 检查 SQLite 连接
    try:
        conn = local_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        results["sqlite"] = True
        logger.info("SQLite 连接检查通过")
    except Exception as e:
        logger.error(f"SQLite 连接检查失败: {e}")
    
    return results


def check_directories():
    """检查必要的目录"""
    directories = ["state", "logs"]
    
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                logger.info(f"创建目录: {directory}")
            except Exception as e:
                logger.error(f"创建目录 {directory} 失败: {e}")
                return False
    
    return True


def health_check():
    """完整的健康检查"""
    logger.info("开始健康检查...")
    
    checks = {
        "config": validate_config(),
        "directories": check_directories(),
        "databases": all(check_database_connections().values())
    }
    
    if all(checks.values()):
        logger.info("健康检查全部通过")
        return True
    else:
        failed_checks = [k for k, v in checks.items() if not v]
        logger.error(f"健康检查失败: {failed_checks}")
        return False


if __name__ == "__main__":
    health_check()