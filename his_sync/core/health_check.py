"""
健康检查模块
"""
import yaml
import os
from core.db_sqlite import get_conn as local_conn
from core.db_factory import get_his_conn
from core.logger import logger


def load_config():
    """加载配置文件"""
    with open("config/config.yaml", 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def validate_config():
    """验证配置文件"""
    try:
        cfg = load_config()
        
        # 检查必需的配置项
        if "active_hospital" not in cfg:
            raise ValueError("配置文件缺少 active_hospital 配置")
            
        if "hospitals" not in cfg:
            raise ValueError("配置文件缺少 hospitals 部分")
            
        if "sqlite" not in cfg:
            raise ValueError("配置文件缺少 sqlite 部分")
            
        if "sync" not in cfg:
            raise ValueError("配置文件缺少 sync 部分")
        
        # 检查激活的医院配置
        active_hospital = cfg["active_hospital"]
        if active_hospital not in cfg["hospitals"]:
            raise ValueError(f"激活的医院 {active_hospital} 在 hospitals 配置中不存在")
        
        hospital_config = cfg["hospitals"][active_hospital]
        required_keys = {
            "his": ["host", "port", "user", "password", "db"],
            "view": ["patient"]
        }
        
        for section, keys in required_keys.items():
            if section not in hospital_config:
                raise ValueError(f"激活医院 {active_hospital} 配置缺少 {section} 部分")
            
            for key in keys:
                if key not in hospital_config[section]:
                    raise ValueError(f"激活医院 {active_hospital} 配置 {section} 部分缺少 {key} 配置")
        
        if "adapter" not in hospital_config:
            raise ValueError(f"激活医院 {active_hospital} 配置缺少 adapter 配置")
        
        # 验证同步间隔
        if cfg["sync"]["interval"] < 60:
            logger.warning("同步间隔小于60秒，可能会对数据库造成压力")
        
        logger.info(f"配置文件验证通过，当前激活医院: {hospital_config.get('name', active_hospital)}")
        return True
        
    except Exception as e:
        logger.error(f"配置文件验证失败: {e}")
        return False


def check_database_connections():
    """检查数据库连接"""
    cfg = load_config()
    results = {"sqlite": False, "his": False}
    
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
    
    # 检查当前激活医院的 HIS 连接
    try:
        active_hospital = cfg["active_hospital"]
        hospital_config = cfg["hospitals"][active_hospital]
        hospital_name = hospital_config["name"]
        
        conn = get_his_conn(hospital_config)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        results["his"] = True
        logger.info(f"{hospital_name} HIS 连接检查通过")
    except Exception as e:
        logger.error(f"HIS 连接检查失败: {e}")
    
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
        "directories": check_directories()
    }
    
    # 检查数据库连接
    db_results = check_database_connections()
    checks["sqlite"] = db_results["sqlite"]
    checks["his"] = db_results["his"]
    
    if all(checks.values()):
        logger.info("健康检查全部通过")
        return True
    else:
        failed_checks = [k for k, v in checks.items() if not v]
        logger.error(f"健康检查失败: {failed_checks}")
        return False


if __name__ == "__main__":
    health_check()