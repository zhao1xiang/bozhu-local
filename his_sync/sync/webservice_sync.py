"""
WebService 同步模块 - 智业集成平台 GetResiVisitRecord 接口
按月拉取住院患者数据，upsert 到本地 SQLite
"""
import json
import yaml
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from contextlib import contextmanager

from core.db_sqlite import get_conn as local_conn
from core.logger import logger

STATE_FILE = "state/sync_state.json"
CONFIG_FILE = "config/config.yaml"


def load_state():
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        logger.error(f"加载状态文件失败: {e}")
        return {}


def save_state(state):
    try:
        with open(STATE_FILE, "w", encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"保存状态文件失败: {e}")


def load_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def build_msg_header(server_name: str, call_operator: str, certificate: str) -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<root>
    <serverName>{server_name}</serverName>
    <format>xml</format>
    <callOperator>{call_operator}</callOperator>
    <certificate>{certificate}</certificate>
</root>"""


def build_msg_body(in_start: str, in_end: str,
                   patient_id: str = "", visit_no: str = "",
                   out_start: str = "", out_end: str = "") -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<root>
    <patientId>{patient_id}</patientId>
    <visitNo>{visit_no}</visitNo>
    <inStartTime>{in_start}</inStartTime>
    <inEndTime>{in_end}</inEndTime>
    <outStartTime>{out_start}</outStartTime>
    <outEndTime>{out_end}</outEndTime>
</root>"""


def call_webservice(wsdl_url: str, msg_header: str, msg_body: str) -> str:
    """
    调用 WebService 接口，返回 XML 字符串
    优先使用 zeep，回退到 suds，最后用 requests 直接发 SOAP
    """
    # 方式1：zeep
    try:
        from zeep import Client
        client = Client(wsdl_url)
        result = client.service.CallInterface(msgHeader=msg_header, msgBody=msg_body)
        return result
    except ImportError:
        logger.debug("zeep 未安装，尝试 suds")
    except Exception as e:
        logger.warning(f"zeep 调用失败: {e}，尝试其他方式")

    # 方式2：suds
    try:
        from suds.client import Client as SudsClient
        client = SudsClient(wsdl_url)
        result = client.service.CallInterface(msgHeader=msg_header, msgBody=msg_body)
        return str(result)
    except ImportError:
        logger.debug("suds 未安装，尝试 requests SOAP")
    except Exception as e:
        logger.warning(f"suds 调用失败: {e}，尝试 requests")

    # 方式3：直接发 SOAP XML（使用内置 http.client，无需第三方库）
    import http.client
    import urllib.parse

    soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:ws="http://ws.service.platform.zysoft.com/">
    <soapenv:Header/>
    <soapenv:Body>
        <ws:CallInterface>
            <msgHeader><![CDATA[{msg_header}]]></msgHeader>
            <msgBody><![CDATA[{msg_body}]]></msgBody>
        </ws:CallInterface>
    </soapenv:Body>
</soapenv:Envelope>"""

    # 去掉 ?wsdl 后缀得到实际服务地址
    service_url = wsdl_url.replace("?wsdl", "")
    parsed = urllib.parse.urlparse(service_url)
    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    path = parsed.path or "/"

    body_bytes = soap_body.encode("utf-8")
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": '""',
        "Content-Length": str(len(body_bytes)),
    }

    if parsed.scheme == "https":
        conn = http.client.HTTPSConnection(host, port, timeout=30)
    else:
        conn = http.client.HTTPConnection(host, port, timeout=30)

    conn.request("POST", path, body=body_bytes, headers=headers)
    resp = conn.getresponse()
    resp_body = resp.read().decode("utf-8", errors="replace")
    conn.close()

    if resp.status != 200:
        raise RuntimeError(f"SOAP 请求失败，HTTP {resp.status}: {resp_body[:200]}")

    logger.debug(f"SOAP 原始响应 (前500字符): {resp_body[:500]}")

    # 从 SOAP 响应中提取 return/payload 节点内容
    import html
    root = ET.fromstring(resp_body)
    for elem in root.iter():
        local_tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
        if local_tag in ("return", "CallInterfaceResult", "payload"):
            text = elem.text or ""
            # 如果内容是 HTML 实体编码，先 unescape
            if "&lt;" in text or "&amp;" in text:
                text = html.unescape(text)
            logger.info(f"找到 {local_tag} 节点，内容前300字符: {text[:300]}")
            return text
    logger.warning(f"未找到 return/payload 节点，返回完整响应")
    return resp_body


def parse_response(xml_str: str) -> list:
    """解析返回的 XML，提取 returnContent 列表"""
    if not xml_str:
        logger.warning("parse_response: 收到空字符串")
        return []
    logger.info(f"parse_response 收到内容 (前300字符): {xml_str[:300]}")
    try:
        # 去掉可能的 XML 声明头再解析
        clean = xml_str.strip()
        if clean.startswith("<?xml"):
            clean = clean[clean.index("?>") + 2:].strip()
        root = ET.fromstring(clean)
        records = []
        for content in root.findall(".//returnContent"):
            record = {}
            for child in content:
                record[child.tag] = (child.text or "").strip()
            records.append(record)
        logger.info(f"parse_response 解析到 {len(records)} 条记录")
        return records
    except ET.ParseError as e:
        logger.error(f"XML 解析失败: {e}\n原始内容: {xml_str[:500]}")
        return []


def upsert_patient_ws(cur, p: dict):
    """按 outpatient_number (visitNo) upsert 患者"""
    outpatient_number = p.get("outpatient_number")
    name = p.get("name", "")
    medical_card_number = p.get("medical_card_number")
    diagnosis = p.get("diagnosis")
    now = datetime.now().isoformat()

    if not outpatient_number:
        return "skipped"

    cur.execute("SELECT id FROM patient WHERE outpatient_number=? AND is_deleted=0",
                (outpatient_number,))
    row = cur.fetchone()

    if row:
        # 更新：只更新姓名、诊断、medical_card_number
        fields = ["name=?", "updated_at=?"]
        values = [name, now]
        if medical_card_number:
            fields.append("medical_card_number=?")
            values.append(medical_card_number)
        if diagnosis:
            fields.append("diagnosis=?")
            values.append(diagnosis)
        values.append(outpatient_number)
        cur.execute(f"UPDATE patient SET {', '.join(fields)} WHERE outpatient_number=? AND is_deleted=0",
                    values)
        return "updated"
    else:
        cur.execute("""
            INSERT INTO patient
            (id, name, outpatient_number, medical_card_number, phone,
             diagnosis, patient_type, left_eye, right_eye, injection_count,
             status, is_deleted, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            str(uuid.uuid4()), name, outpatient_number, medical_card_number,
            None, diagnosis, None, 0, 0, None,
            'active', 0, now, now
        ))
        return "inserted"


def sync_webservice():
    """
    主同步函数：按月拉取最近数据，upsert 到本地 DB
    """
    state = load_state()
    cfg = load_config()

    # 找到 webservice 类型的医院配置
    ws_hospitals = {
        k: v for k, v in cfg.get("hospitals", {}).items()
        if v.get("his", {}).get("type") == "webservice"
    }

    if not ws_hospitals:
        logger.debug("没有配置 webservice 类型的医院，跳过")
        return

    local_db = local_conn()
    local_cursor = local_db.cursor()

    try:
        for hospital_id, hospital_config in ws_hospitals.items():
            _sync_one_hospital(hospital_id, hospital_config, state, local_cursor, local_db)
    finally:
        local_db.close()

    save_state(state)


def _sync_one_hospital(hospital_id: str, hospital_config: dict,
                       state: dict, local_cursor, local_db):
    """同步单个 WebService 医院"""
    his = hospital_config["his"]
    hospital_name = hospital_config["name"]
    wsdl_url = his["url"]
    call_operator = his["call_operator"]
    certificate = his["certificate"]
    server_name = his.get("server_name", "GetResiVisitRecord")
    adapter_name = hospital_config.get("adapter", "hospital3_adapter")

    # 加载适配器
    if adapter_name == "hospital3_adapter":
        from adapter.hospital3_adapter import convert_patient
    else:
        from core.db_factory import get_adapter
        convert_patient = get_adapter(adapter_name)

    # 时间范围：固定从 2026-04-15 开始，到当天结束
    today = datetime.now()
    in_start = today.strftime("%Y-04-15 00:00:00")
    in_end = today.strftime("%Y-%m-%d 23:59:59")

    logger.info(f"[{hospital_name}] 同步时间范围: {in_start} ~ {in_end}")

    msg_header = build_msg_header(server_name, call_operator, certificate)
    msg_body = build_msg_body(in_start, in_end)

    try:
        xml_result = call_webservice(wsdl_url, msg_header, msg_body)
        records = parse_response(xml_result)
        logger.info(f"[{hospital_name}] 获取到 {len(records)} 条记录")
    except Exception as e:
        logger.error(f"[{hospital_name}] WebService 调用失败: {e}")
        return

    stats = {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}

    for i, row in enumerate(records, 1):
        try:
            patient_data = convert_patient(row)
            if patient_data is None:
                stats["skipped"] += 1
                continue
            op = upsert_patient_ws(local_cursor, patient_data)
            stats[op] = stats.get(op, 0) + 1
        except Exception as e:
            logger.error(f"[{hospital_name}] 处理第 {i} 条记录失败: {e}")
            stats["errors"] += 1

    local_db.commit()

    # 更新状态
    state[f"ws_{hospital_id}_last_sync"] = today.isoformat()
    state[f"ws_{hospital_id}_last_stats"] = stats

    logger.info(f"[{hospital_name}] 同步完成 - 新增:{stats['inserted']} 更新:{stats['updated']} "
                f"跳过:{stats['skipped']} 错误:{stats['errors']}")
