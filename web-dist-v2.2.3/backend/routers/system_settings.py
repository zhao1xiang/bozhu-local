from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import engine
from models import SystemSetting, SystemSettingCreate, SystemSettingUpdate
from typing import List

router = APIRouter(prefix="/system-settings", tags=["system-settings"])

def get_session():
    with Session(engine) as session:
        yield session

@router.get("/", response_model=List[SystemSetting])
def read_settings(session: Session = Depends(get_session)):
    settings = session.exec(select(SystemSetting)).all()
    return settings

@router.get("/{key}", response_model=SystemSetting)
def read_setting(key: str, session: Session = Depends(get_session)):
    setting = session.exec(select(SystemSetting).where(SystemSetting.key == key)).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting

@router.post("/", response_model=SystemSetting)
def create_setting(setting: SystemSettingCreate, session: Session = Depends(get_session)):
    db_setting = SystemSetting.model_validate(setting)
    session.add(db_setting)
    session.commit()
    session.refresh(db_setting)
    return db_setting

@router.put("/{key}", response_model=SystemSetting)
def update_setting(key: str, setting_update: SystemSettingUpdate, session: Session = Depends(get_session)):
    db_setting = session.exec(select(SystemSetting).where(SystemSetting.key == key)).first()
    if not db_setting:
        # Create if not exists ? Or error? Let's create if not exists for convenience
        new_setting = SystemSetting(key=key, value=setting_update.value, description=setting_update.description)
        session.add(new_setting)
        session.commit()
        session.refresh(new_setting)
        return new_setting
    
    if setting_update.value is not None:
        db_setting.value = setting_update.value
    if setting_update.description is not None:
        db_setting.description = setting_update.description
        
    session.add(db_setting)
    session.commit()
    session.refresh(db_setting)
    return db_setting
