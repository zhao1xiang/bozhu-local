from sqlmodel import SQLModel, Field
from typing import Optional


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    # role: admin = 管理员，doctor = 医生账号
    role: str = Field(default="admin")
    # 绑定的医生名称（与数据字典中的 doctor value 对应）；admin 为空表示可查看所有
    doctor: Optional[str] = Field(default=None)
    # 兼容旧字段 wards（保留不删，避免数据库迁移问题）
    wards: Optional[str] = Field(default=None)
