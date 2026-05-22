"""
用户管理接口（仅管理员可用）
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import engine
from models.user import User
from security import get_current_user, get_password_hash, get_session
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/users", tags=["users"])


def require_admin(current_user: User = Depends(get_current_user)):
    if getattr(current_user, 'role', 'admin') != 'admin':
        raise HTTPException(status_code=403, detail="仅管理员可操作")
    return current_user


class UserOut(BaseModel):
    id: int
    username: str
    is_active: bool
    role: str
    doctor: Optional[str] = None
    wards: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "doctor"
    doctor: Optional[str] = None
    wards: Optional[str] = None


class UserUpdate(BaseModel):
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None
    doctor: Optional[str] = None
    wards: Optional[str] = None


@router.get("/", response_model=List[UserOut])
def list_users(
    session: Session = Depends(get_session),
    doctor: Optional[str] = None,
    role: Optional[str] = None,
    _: User = Depends(require_admin),
):
    query = select(User)
    if doctor:
        query = query.where(User.doctor == doctor)
    if role:
        query = query.where(User.role == role)
    users = session.exec(query).all()
    return [UserOut(
        id=u.id,
        username=u.username,
        is_active=getattr(u, 'is_active', True),
        role=getattr(u, 'role', 'admin'),
        doctor=getattr(u, 'doctor', None),
        wards=getattr(u, 'wards', None),
    ) for u in users]


@router.post("/", response_model=UserOut)
def create_user(
    body: UserCreate,
    session: Session = Depends(get_session),
    _: User = Depends(require_admin),
):
    existing = session.exec(select(User).where(User.username == body.username)).first()
    if existing:
        raise HTTPException(status_code=409, detail="用户名已存在")
    user = User(
        username=body.username,
        hashed_password=get_password_hash(body.password),
        is_active=True,
        role=body.role,
        doctor=body.doctor,
        wards=body.wards,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserOut(
        id=user.id, username=user.username,
        is_active=getattr(user, 'is_active', True),
        role=getattr(user, 'role', 'doctor'),
        doctor=getattr(user, 'doctor', None),
        wards=getattr(user, 'wards', None),
    )


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    body: UserUpdate,
    session: Session = Depends(get_session),
    _: User = Depends(require_admin),
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if body.password:
        user.hashed_password = get_password_hash(body.password)
    if body.is_active is not None:
        user.is_active = body.is_active
    if body.role is not None:
        user.role = body.role
    if body.doctor is not None:
        user.doctor = body.doctor
    if body.wards is not None:
        user.wards = body.wards
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserOut(
        id=user.id, username=user.username,
        is_active=getattr(user, 'is_active', True),
        role=getattr(user, 'role', 'doctor'),
        doctor=getattr(user, 'doctor', None),
        wards=getattr(user, 'wards', None),
    )


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.username == 'admin':
        raise HTTPException(status_code=400, detail="不能删除 admin 账号")
    session.delete(user)
    session.commit()
    return {"message": "删除成功"}
