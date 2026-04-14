import json
import yaml
import uuid
from datetime import datetime
from contextlib import contextmanager

from core.db_sqlite import get_conn as local_conn
from core.db_factory import get_his_conn, get_adapter
from core.logger import logger


STATE_FILE = "state/sync_state.json"
CONFIG_FILE = "config/config.yaml"


def load_state():
    """加载同步状态"""
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"状态文件 {STATE_FILE} 不存在，使用默认状态")
        return {}
    except Exception as e:
        logger.error(f"加载状态文件失败: {e}")
        return {}


def save_state(state):
    """保存同步状态"""
    try:
        with open(STATE_FILE, "w", encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        logger.debug("状态文件保存成功")
    except Exception as e:
        logger.error(f"保存状态文件失败: {e}")


def load_config():
    """加载配置文件"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_active_hospital_config():
    """获取当前激活的医院配置"""
    cfg = load_config()
    active_hospital = cfg.get("active_hospital")
    
    if not active_hospital:
        raise ValueError("配置文件中未指定 active_hospital")
    
    if active_hospital not in cfg["hospitals"]:
        raise ValueError(f"未找到医院配置: {active_hospital}")
    
    hospital_config = cfg["hospitals"][active_hospital]
    hospital_config["id"] = active_hospital  # 添加医院ID
    
    logger.info(f"当前激活医院: {hospital_config['name']} ({active_hospital})")
    return hospital_config


@contextmanager
def get_db_connections():
    """数据库连接上下文管理器"""
    his_conn_obj = None
    local_conn_obj = None
    his_cursor = None
    local_cursor = None
    
    try:
        # 获取当前激活医院配置
        hospital_config = get_active_hospital_config()
        
        # 建立连接
        his_conn_obj = get_his_conn(hospital_config)
        local_conn_obj = local_conn()
        his_cursor = his_conn_obj.cursor()
        local_cursor = local_conn_obj.cursor()
        
        yield his_cursor, local_cursor, local_conn_obj, hospital_config
        
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
    支持不同医院的字段
    """
    outpatient_number = p.get("outpatient_number")
    name = p.get("name", "")
    medical_card_number = p.get("medical_card_number")
    phone = p.get("phone")
    diagnosis = p.get("diagnosis")
    patient_type = p.get("patient_type")
    left_eye = p.get("left_eye")
    right_eye = p.get("right_eye")
    injection_count = p.get("injection_count")

    if outpatient_number:
        # 检查是否存在
        cur.execute(
            "SELECT id FROM patient WHERE outpatient_number=?",
            (outpatient_number,)
        )
        exists = cur.fetchone()

        if exists:
            # 更新现有记录
            update_fields = ["name=?", "updated_at=?"]
            update_values = [name, datetime.now()]

            # medical_card_number 总是更新
            update_fields.append("medical_card_number=?")
            update_values.append(medical_card_number)

            # phone 为空时不更新
            if phone:
                update_fields.append("phone=?")
                update_values.append(phone)

            # diagnosis 为空时不更新
            if diagnosis:
                update_fields.append("diagnosis=?")
                update_values.append(diagnosis)

            # patient_type 为空时不更新
            if patient_type:
                update_fields.append("patient_type=?")
                update_values.append(patient_type)

            # left_eye/right_eye 不为 None 时更新
            if left_eye is not None:
                update_fields.append("left_eye=?")
                update_values.append(left_eye)
            if right_eye is not None:
                update_fields.append("right_eye=?")
                update_values.append(right_eye)

            # injection_count 有值时更新
            if injection_count is not None:
                update_fields.append("injection_count=?")
                update_values.append(injection_count)
            
            update_values.append(outpatient_number)  # WHERE 条件
            
            sql = f"""
                UPDATE patient
                SET {', '.join(update_fields)}
                WHERE outpatient_number=?
            """
            cur.execute(sql, update_values)
            return "updated"
        else:
            # 插入新记录
            cur.execute(
                """
                INSERT INTO patient
                (id, name, outpatient_number, medical_card_number, phone, 
                 diagnosis, patient_type, left_eye, right_eye, injection_count, status, created_at, updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    str(uuid.uuid4()),
                    name,
                    outpatient_number,
                    medical_card_number,
                    phone,
                    diagnosis,
                    patient_type,
                    left_eye if left_eye is not None else False,
                    right_eye if right_eye is not None else False,
                    injection_count,
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
            (id, name, outpatient_number, medical_card_number, phone,
             diagnosis, patient_type, left_eye, right_eye, injection_count, status, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                str(uuid.uuid4()),
                name,
                None,
                medical_card_number,
                phone,
                diagnosis,
                patient_type,
                left_eye if left_eye is not None else False,
                right_eye if right_eye is not None else False,
                injection_count,
                'active',
                datetime.now(),
                datetime.now()
            )
        )
        return "inserted"


def sync_patient():
    """同步当前激活医院的患者数据"""
    try:
        state = load_state()
        
        logger.info("开始患者数据同步")
        
        with get_db_connections() as (his_cursor, local_cursor, local_conn, hospital_config):
            hospital_name = hospital_config["name"]
            hospital_id = hospital_config["id"]
            view = hospital_config["view"]["patient"]
            adapter_name = hospital_config["adapter"]
            
            # 获取适配器
            convert_patient = get_adapter(adapter_name)
            
            # 查询源数据
            logger.debug(f"查询 {hospital_name} 视图: {view}")
            his_cursor.execute(f"SELECT * FROM {view}")
            
            # 获取列名
            columns = [column[0] for column in his_cursor.description]
            
            # 获取数据并转换为字典格式
            rows = []
            for row in his_cursor.fetchall():
                row_dict = dict(zip(columns, row))
                rows.append(row_dict)
            
            if not rows:
                logger.info(f"{hospital_name} 源数据为空，跳过同步")
                return
                
            logger.info(f"从 {hospital_name} 获取到 {len(rows)} 条记录")
            
            # 统计操作结果
            stats = {"inserted": 0, "updated": 0, "errors": 0}
            
            # 处理每条记录
            for i, row in enumerate(rows, 1):
                try:
                    patient_data = convert_patient(row)
                    if patient_data is None:
                        # 适配器返回 None 表示跳过此记录
                        continue
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
            state["active_hospital"] = hospital_id
            state["hospital_name"] = hospital_name
            state["last_sync_time"] = datetime.now().isoformat()
            state["last_sync_stats"] = stats
            state["last_sync_count"] = len(rows)
            save_state(state)
            
            logger.info(f"{hospital_name} 同步完成 - 新增: {stats['inserted']}, 更新: {stats['updated']}, 错误: {stats['errors']}")
            
    except Exception as e:
        logger.error(f"同步过程发生错误: {e}", exc_info=True)
        raise