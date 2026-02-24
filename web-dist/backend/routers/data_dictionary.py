from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from database import engine
from models import DataDictionary, DataDictionaryBase
from typing import List, Optional

router = APIRouter(prefix="/data-dictionary", tags=["data-dictionary"])

def get_session():
    with Session(engine) as session:
        yield session

@router.post("/", response_model=DataDictionary)
def create_item(item: DataDictionaryBase, session: Session = Depends(get_session)):
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
    query = select(DataDictionary)
    if category:
        query = query.where(DataDictionary.category == category)
    query = query.order_by(DataDictionary.sort_order, DataDictionary.created_at)
    items = session.exec(query).all()
    return items

@router.put("/{item_id}", response_model=DataDictionary)
def update_item(item_id: str, item: DataDictionaryBase, session: Session = Depends(get_session)):
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
def delete_item(item_id: str, session: Session = Depends(get_session)):
    db_item = session.get(DataDictionary, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    session.delete(db_item)
    session.commit()
    return {"ok": True}
