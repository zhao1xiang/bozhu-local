from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from database import engine
from models.user import User
from security import verify_password, create_access_token, get_password_hash, get_current_user, get_session
from datetime import timedelta
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class Token(BaseModel):
    access_token: str
    token_type: str

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_expires = timedelta(minutes=30 * 24 * 60) # 30 days
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="旧密码错误")
    
    current_user.hashed_password = get_password_hash(password_data.new_password)
    session.add(current_user)
    session.commit()
    return {"message": "密码修改成功"}

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
