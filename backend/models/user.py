from sqlmodel import SQLModel, Field
from typing import Optional


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    # role: admin = 管理员，ward = 病区账号
    role: str = Field(default="admin")
    # 病区列表，逗号分隔，如 "1,2"；admin 为空表示可查看所有
    wards: Optional[str] = Field(default=None)
