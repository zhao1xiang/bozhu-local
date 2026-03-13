from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
import uuid

class DataDictionaryBase(SQLModel):
    category: str = Field(index=True) # e.g., "doctor"
    value: str # The actual value to store
    label: str # The display label
    sort_order: int = 0
    is_active: bool = True

class DataDictionary(DataDictionaryBase, table=True):
    __tablename__ = "data_dictionary"
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
