from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import engine
from models import SystemSetting, SystemSettingCreate, SystemSettingUpdate
from models.user import User
from security import get_current_user
from typing import List

router = APIRouter(prefix="/system-settings", tags=["system-settings"])

def get_session():
    with Session(engine) as session:
        yield session

def require_admin(current_user: User = Depends(get_current_user)):
    """检查用户是否为管理员"""
    if getattr(current_user, 'role', 'admin') != 'admin':
        raise HTTPException(status_code=403, detail="仅管理员可操作")
    return current_user

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
def create_setting(
    setting: SystemSettingCreate, 
    session: Session = Depends(get_session),
    _: User = Depends(require_admin),
):
    db_setting = SystemSetting.model_validate(setting)
    session.add(db_setting)
    session.commit()
    session.refresh(db_setting)
    return db_setting

@router.put("/{key}", response_model=SystemSetting)
def update_setting(
    key: str, 
    setting_update: SystemSettingUpdate, 
    session: Session = Depends(get_session),
    _: User = Depends(require_admin),
):
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
