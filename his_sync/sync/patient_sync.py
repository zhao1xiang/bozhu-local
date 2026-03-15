import json
import yaml
import uuid
from datetime import datetime
from contextlib import contextmanager

from core.db_mssql import get_conn as his_conn
from core.db_sqlite import get_conn as local_conn
from adapter.vegf_adapter import convert_patient
from core.logger import logger


STATE_FILE = "state/sync_state.json"
CONFIG_FILE = "config/config.yaml"


def load_state():
    """加载同步状态"""
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"状态文件 {STATE_FILE} 不存在，使用默认状态")
        return {"patient_last_sync_count": 0}
    except Exception as e:
        logger.error(f"加载状态文件失败: {e}")
        return {"patient_last_sync_count": 0}


def save_state(state):
    """保存同步状态"""
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
        logger.debug("状态文件保存成功")
    except Exception as e:
        logger.error(f"保存状态文件失败: {e}")


def load_config():
    """加载配置文件"""
    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f)


@contextmanager
def get_db_connections():
    """数据库连接上下文管理器"""
    his_conn_obj = None
    local_conn_obj = None
    his_cursor = None
    local_cursor = None
    
    try:
        # 建立连接
        his_conn_obj = his_conn()
        local_conn_obj = local_conn()
        his_cursor = his_conn_obj.cursor(as_dict=True)
        local_cursor = local_conn_obj.cursor()
        
        yield his_cursor, local_cursor, local_conn_obj
        
    except Exception as e:
        logger.error(f"数据库连接错误: {e}")
        if local_conn_obj:
            local_conn_obj.rollback()
        raise
    finally:
        # 确保连接被关闭
        if his_cursor:
            his_cursor.close()
        if his_conn_obj:
            his_conn_obj.close()
        if local_conn_obj:
            local_conn_obj.close()
        logger.debug("数据库连接已关闭")


def upsert_patient(cur, p):
    """
    根据 outpatient_number 判断插入或更新
    """
    outpatient_number = p.get("outpatient_number")
    name = p.get("name", "")

    if outpatient_number:
        # 检查是否存在
        cur.execute(
            "SELECT id FROM patient WHERE outpatient_number=?",
            (outpatient_number,)
        )
        exists = cur.fetchone()

        if exists:
            # 更新现有记录
            cur.execute(
                """
                UPDATE patient
                SET name=?, updated_at=?
                WHERE outpatient_number=?
                """,
                (name, datetime.now(), outpatient_number)
            )
            return "updated"
        else:
            # 插入新记录
            cur.execute(
                """
                INSERT INTO patient
                (id, name, outpatient_number, left_eye, right_eye, status, created_at, updated_at)
                VALUES (?,?,?,?,?,?,?,?)
                """,
                (
                    str(uuid.uuid4()),
                    name,
                    outpatient_number,
                    False,
                    False,
                    'active',
                    datetime.now(),
                    datetime.now()
                )
            )
            return "inserted"
    else:
        # 没有门诊号，直接插入
        cur.execute(
            """
            INSERT INTO patient
            (id, name, outpatient_number, left_eye, right_eye, status, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?)
            """,
            (
                str(uuid.uuid4()),
                name,
                None,
                False,
                False,
                'active',
                datetime.now(),
                datetime.now()
            )
        )
        return "inserted"


def sync_patient():
    """同步患者数据"""
    try:
        state = load_state()
        cfg = load_config()
        view = cfg["view"]["patient"]
        
        logger.info("开始患者数据同步")
        
        with get_db_connections() as (his_cursor, local_cursor, local_conn):
            # 查询源数据
            logger.debug(f"查询视图: {view}")
            his_cursor.execute(f"SELECT * FROM {view}")
            rows = his_cursor.fetchall()
            
            if not rows:
                logger.info("源数据为空，跳过同步")
                return
                
            logger.info(f"从源数据库获取到 {len(rows)} 条记录")
            
            # 统计操作结果
            stats = {"inserted": 0, "updated": 0, "errors": 0}
            
            # 处理每条记录
            for i, row in enumerate(rows, 1):
                try:
                    patient_data = convert_patient(row)
                    operation = upsert_patient(local_cursor, patient_data)
                    stats[operation] += 1
                    
                    if i % 100 == 0:  # 每100条记录记录一次进度
                        logger.debug(f"已处理 {i}/{len(rows)} 条记录")
                        
                except Exception as e:
                    logger.error(f"处理第 {i} 条记录失败: {e}")
                    stats["errors"] += 1
                    continue
            
            # 提交事务
            local_conn.commit()
            
            # 更新状态
            state["patient_last_sync_count"] = len(rows)
            state["last_sync_time"] = datetime.now().isoformat()
            state["last_sync_stats"] = stats
            save_state(state)
            
            logger.info(f"同步完成 - 新增: {stats['inserted']}, 更新: {stats['updated']}, 错误: {stats['errors']}")
            
    except Exception as e:
        logger.error(f"同步过程发生错误: {e}", exc_info=True)
        raise