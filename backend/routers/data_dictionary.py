from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from sqlalchemy import text
from database import engine
from models import DataDictionary, DataDictionaryBase
from models.user import User
from security import get_current_user
from typing import List, Optional
from datetime import datetime, timezone

router = APIRouter(prefix="/data-dictionary", tags=["data-dictionary"])

def get_session():
    with Session(engine) as session:
        yield session

def require_admin(current_user: User = Depends(get_current_user)):
    """检查用户是否为管理员"""
    if getattr(current_user, 'role', 'admin') != 'admin':
        raise HTTPException(status_code=403, detail="仅管理员可操作")
    return current_user


def _safe_datetime(value):
    if value is None or str(value).strip() == "":
        return datetime.now(timezone.utc)
    if isinstance(value, datetime):
        return value
    text_value = str(value).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(text_value[:len(fmt)], fmt)
        except ValueError:
            pass
    try:
        return datetime.fromisoformat(text_value)
    except Exception:
        return datetime.now(timezone.utc)


def _safe_bool(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return True
    return str(value).strip().lower() not in ("0", "false", "no", "n", "否")


def _dict_row_to_dict(row):
    data = dict(row._mapping)
    data["sort_order"] = int(data.get("sort_order") or 0)
    data["is_active"] = _safe_bool(data.get("is_active"))
    data["created_at"] = _safe_datetime(data.get("created_at"))
    return data

@router.post("/", response_model=DataDictionary)
def create_item(
    item: DataDictionaryBase, 
    session: Session = Depends(get_session),
    _: User = Depends(require_admin),
):
    db_item = DataDictionary.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

@router.get("/", response_model=List[DataDictionary])
def read_items(
    category: Optional[str] = None, 
    session: Session = Depends(get_session)
):
    where_clause = ""
    params = {}
    if category:
        where_clause = "WHERE category = :category"
        params["category"] = category
    rows = session.execute(text(f"""
        SELECT id, category, value, label, sort_order, is_active, extra, ward, created_at
        FROM data_dictionary
        {where_clause}
        ORDER BY COALESCE(sort_order, 0), datetime(created_at)
    """), params).all()
    return [_dict_row_to_dict(row) for row in rows]

@router.put("/{item_id}", response_model=DataDictionary)
def update_item(
    item_id: str, 
    item: DataDictionaryBase, 
    session: Session = Depends(get_session),
    _: User = Depends(require_admin),
):
    db_item = session.get(DataDictionary, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item_data = item.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(db_item, key, value)
        
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

@router.delete("/{item_id}")
def delete_item(
    item_id: str, 
    session: Session = Depends(get_session),
    _: User = Depends(require_admin),
):
    db_item = session.get(DataDictionary, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    session.delete(db_item)
    session.commit()
    return {"ok": True}
