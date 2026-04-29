from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
import uuid


class EmbedLog(SQLModel, table=True):
    __tablename__ = "embed_log"

    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    # 调用类型：verify / verify-plain
    call_type: str = Field(index=True)
    # 完整 URL（含参数）
    url: Optional[str] = Field(default=None)
    # 原始参数（JSON 字符串）
    params: Optional[str] = Field(default=None)
    # 解析出的门诊号
    outpatient_number: Optional[str] = Field(default=None, index=True)
    # 解析出的姓名
    patient_name: Optional[str] = Field(default=None)
    # 客户端 IP
    client_ip: Optional[str] = Field(default=None)
    # 是否成功（签名验证通过 / 参数合法）
    success: bool = Field(default=True)
    # 错误信息
    error_msg: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
