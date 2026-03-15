import sqlite3
import yaml
import os
from core.logger import logger


def get_conn():
    """
    获取 SQLite 连接
    """
    with open("config/config.yaml") as f:
        cfg = yaml.safe_load(f)

    path = cfg["sqlite"]["path"]
    
    # 确保数据库目录存在
    db_dir = os.path.dirname(path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
        logger.info(f"创建数据库目录: {db_dir}")

    try:
        conn = sqlite3.connect(
            path,
            timeout=30.0,  # 设置超时
            check_same_thread=False
        )
        conn.row_factory = sqlite3.Row
        
        # 启用 WAL 模式以提高并发性能
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        
        logger.debug(f"SQLite 连接成功: {path}")
        return conn
        
    except Exception as e:
        logger.error(f"SQLite 连接失败: {e}")
        raise