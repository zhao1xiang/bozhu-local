import json
import yaml
import uuid
import inspect
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
        
        yield his_cursor, local_cursor, local_conn_obj, hospital_config, his_conn_obj
        
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
    drug_type = p.get("drug_type")
    if drug_type:
        logger.info(f"同步患者药品: outpatient_number={outpatient_number}, drug_type={drug_type}")
    left_vision = p.get("left_vision")
    right_vision = p.get("right_vision")
    left_vision_corrected = p.get("left_vision_corrected")
    right_vision_corrected = p.get("right_vision_corrected")
    remarks = p.get("remarks")
    doctor = p.get("doctor")
    yyrq = p.get("yyrq")
    ryrq = p.get("ryrq")

    cur.execute("PRAGMA table_info(patient)")
    existing_columns = {row[1] for row in cur.fetchall()}
    optional_patient_fields = [
        ("yyrq", yyrq),
        ("ryrq", ryrq),
    ]

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

            # drug_type 有值时更新
            if drug_type:
                update_fields.append("drug_type=?")
                update_values.append(drug_type)

            # 视力字段有值时更新
            if left_vision is not None:
                update_fields.append("left_vision=?")
                update_values.append(left_vision)
            if right_vision is not None:
                update_fields.append("right_vision=?")
                update_values.append(right_vision)
            if left_vision_corrected is not None:
                update_fields.append("left_vision_corrected=?")
                update_values.append(left_vision_corrected)
            if right_vision_corrected is not None:
                update_fields.append("right_vision_corrected=?")
                update_values.append(right_vision_corrected)
            if remarks:
                update_fields.append("remarks=?")
                update_values.append(remarks)
            if doctor:
                update_fields.append("doctor=?")
                update_values.append(doctor)
            for column_name, column_value in optional_patient_fields:
                if column_name in existing_columns and column_value:
                    update_fields.append(f"{column_name}=?")
                    update_values.append(column_value)
            
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
                 diagnosis, drug_type, patient_type, left_eye, right_eye, injection_count,
                 left_vision, right_vision, left_vision_corrected, right_vision_corrected,
                 remarks, doctor, status, is_deleted, created_at, updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    str(uuid.uuid4()),
                    name, outpatient_number, medical_card_number, phone,
                    diagnosis, drug_type, patient_type,
                    left_eye if left_eye is not None else False,
                    right_eye if right_eye is not None else False,
                    injection_count,
                    left_vision, right_vision, left_vision_corrected, right_vision_corrected,
                    remarks, doctor,
                    'active', 0,
                    datetime.now(), datetime.now()
                )
            )
            optional_update_fields = []
            optional_update_values = []
            for column_name, column_value in optional_patient_fields:
                if column_name in existing_columns and column_value:
                    optional_update_fields.append(f"{column_name}=?")
                    optional_update_values.append(column_value)
            if optional_update_fields:
                optional_update_values.append(outpatient_number)
                cur.execute(
                    f"UPDATE patient SET {', '.join(optional_update_fields)} WHERE outpatient_number=?",
                    optional_update_values,
                )
            return "inserted"
    else:
        # 没有门诊号，直接插入
        cur.execute(
            """
            INSERT INTO patient
            (id, name, outpatient_number, medical_card_number, phone,
             diagnosis, drug_type, patient_type, left_eye, right_eye, injection_count,
             left_vision, right_vision, left_vision_corrected, right_vision_corrected,
             remarks, doctor, status, is_deleted, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                str(uuid.uuid4()),
                name, None, medical_card_number, phone,
                diagnosis, drug_type, patient_type,
                left_eye if left_eye is not None else False,
                right_eye if right_eye is not None else False,
                injection_count,
                left_vision, right_vision, left_vision_corrected, right_vision_corrected,
                remarks, doctor,
                'active', 0,
                datetime.now(), datetime.now()
            )
        )
        return "inserted"


def upsert_patient(cur, p):
    """Insert or update patient data using only columns that exist locally."""
    outpatient_number = p.get("outpatient_number")
    name = p.get("name", "")
    now = datetime.now()

    cur.execute("PRAGMA table_info(patient)")
    existing_columns = {row[1] for row in cur.fetchall()}

    def has_col(column_name):
        return column_name in existing_columns

    def add_update(fields, values, column_name, column_value, allow_empty=False):
        if has_col(column_name) and (allow_empty or column_value is not None):
            fields.append(f"{column_name}=?")
            values.append(column_value)

    def insert_patient(row_values):
        columns = []
        values = []
        for column_name, column_value in row_values:
            if has_col(column_name):
                columns.append(column_name)
                values.append(column_value)
        placeholders = ",".join(["?"] * len(columns))
        cur.execute(
            f"INSERT INTO patient ({', '.join(columns)}) VALUES ({placeholders})",
            values,
        )

    row_values = [
        ("id", str(uuid.uuid4())),
        ("name", name),
        ("outpatient_number", outpatient_number),
        ("medical_card_number", p.get("medical_card_number")),
        ("phone", p.get("phone")),
        ("diagnosis", p.get("diagnosis")),
        ("drug_type", p.get("drug_type")),
        ("patient_type", p.get("patient_type")),
        ("left_eye", p.get("left_eye") if p.get("left_eye") is not None else False),
        ("right_eye", p.get("right_eye") if p.get("right_eye") is not None else False),
        ("injection_count", p.get("injection_count")),
        ("left_vision", p.get("left_vision")),
        ("right_vision", p.get("right_vision")),
        ("left_vision_corrected", p.get("left_vision_corrected")),
        ("right_vision_corrected", p.get("right_vision_corrected")),
        ("remarks", p.get("remarks")),
        ("doctor", p.get("doctor")),
        ("yyrq", p.get("yyrq")),
        ("ryrq", p.get("ryrq")),
        ("status", "active"),
        ("is_deleted", 0),
        ("created_at", now),
        ("updated_at", now),
    ]

    drug_type = p.get("drug_type")
    if drug_type:
        logger.info(f"同步患者药品: outpatient_number={outpatient_number}, drug_type={drug_type}")

    if outpatient_number:
        cur.execute("SELECT id FROM patient WHERE outpatient_number=?", (outpatient_number,))
        exists = cur.fetchone()
        if exists:
            update_fields = []
            update_values = []
            add_update(update_fields, update_values, "name", name, allow_empty=True)
            add_update(update_fields, update_values, "updated_at", now, allow_empty=True)
            add_update(update_fields, update_values, "medical_card_number", p.get("medical_card_number"), allow_empty=True)

            non_empty_fields = [
                "phone",
                "diagnosis",
                "patient_type",
                "drug_type",
                "remarks",
                "doctor",
                "yyrq",
                "ryrq",
            ]
            for column_name in non_empty_fields:
                column_value = p.get(column_name)
                if column_value:
                    add_update(update_fields, update_values, column_name, column_value)

            nullable_fields = [
                "left_eye",
                "right_eye",
                "injection_count",
                "left_vision",
                "right_vision",
                "left_vision_corrected",
                "right_vision_corrected",
            ]
            for column_name in nullable_fields:
                column_value = p.get(column_name)
                if column_value is not None:
                    add_update(update_fields, update_values, column_name, column_value)

            update_values.append(outpatient_number)
            cur.execute(
                f"UPDATE patient SET {', '.join(update_fields)} WHERE outpatient_number=?",
                update_values,
            )
            return "updated"

    insert_patient(row_values)
    return "inserted"


def sync_patient():
    """同步当前激活医院的患者数据（仅 SQL 视图类型）"""
    try:
        cfg = load_config()
        active_hospital = cfg.get("active_hospital")
        hospital_config = cfg["hospitals"].get(active_hospital, {})
        his_type = hospital_config.get("his", {}).get("type", "mssql")

        # webservice 类型由 sync_webservice 处理，跳过
        if his_type == "webservice":
            logger.debug(f"当前激活医院为 WebService 类型，patient_sync 跳过")
            return
        state = load_state()
        
        logger.info("开始患者数据同步")
        
        with get_db_connections() as (his_cursor, local_cursor, local_conn, hospital_config, his_conn):
            hospital_name = hospital_config["name"]
            hospital_id = hospital_config["id"]
            his_type = hospital_config.get("his", {}).get("type", "mssql")
            adapter_name = hospital_config["adapter"]

            # 获取适配器
            convert_patient = get_adapter(adapter_name)
            adapter_accepts_conn = len(inspect.signature(convert_patient).parameters) >= 2

            # 根据类型查询数据
            if his_type == "cache":
                # Caché 数据库：调用存储过程
                procedure = hospital_config["his"].get("procedure", "")
                if not procedure:
                    logger.error(f"{hospital_name} Caché 类型缺少 procedure 配置")
                    return
                today = datetime.now().strftime("%Y-%m-%d")
                sql = f"CALL {procedure}('{today}', '{today}')"
                logger.debug(f"执行 Caché 存储过程: {sql}")
                his_cursor.execute(sql)
            else:
                # SQL Server/MySQL：查询视图
                view = hospital_config["view"]["patient"]
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
                    if adapter_accepts_conn:
                        patient_data = convert_patient(row, his_conn)
                    else:
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
