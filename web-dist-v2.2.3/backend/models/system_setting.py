from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime

class SystemSettingBase(SQLModel):
    key: str = Field(index=True, unique=True)
    value: str
    description: Optional[str] = None

class SystemSetting(SystemSettingBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    updated_at: datetime = Field(default_factory=datetime.now)

class SystemSettingCreate(SystemSettingBase):
    pass

class SystemSettingUpdate(SQLModel):
    value: Optional[str] = None
    description: Optional[str] = None
