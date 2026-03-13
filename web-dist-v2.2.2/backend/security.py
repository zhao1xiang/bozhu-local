from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from database import engine
from models.user import User
import hashlib
import base64
import secrets

# Secret key for JWT (should be environmental variable in production)
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60 # 30 days

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# 兼容旧版本：同时支持 bcrypt 和 PBKDF2 两种密码格式
def verify_password(plain_password, hashed_password):
    """验证密码 - 兼容 bcrypt 和 PBKDF2 两种格式"""
    
    # 检查是否是 bcrypt 格式（旧版本）
    if hashed_password.startswith('$2b$') or hashed_password.startswith('$2a$'):
        # 使用 bcrypt 验证（需要 passlib）
        try:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            return pwd_context.verify(plain_password, hashed_password)
        except ImportError:
            # 如果没有 passlib/bcrypt，返回 False
            # 这种情况下，用户需要重置密码
            print("警告：检测到 bcrypt 格式密码，但 bcrypt 库不可用")
            return False
        except Exception as e:
            print(f"bcrypt 验证失败: {e}")
            return False
    
    # PBKDF2 格式（新版本）
    try:
        # 解析存储的哈希值
        parts = hashed_password.split('$')
        if len(parts) != 3:
            return False
        
        algorithm, salt_b64, hash_b64 = parts
        salt = base64.b64decode(salt_b64)
        stored_hash = base64.b64decode(hash_b64)
        
        # 使用相同的盐值计算新密码的哈希
        new_hash = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode('utf-8'),
            salt,
            100000  # 迭代次数
        )
        
        # 比较哈希值
        return new_hash == stored_hash
    except Exception:
        return False

def get_password_hash(password):
    """生成密码哈希 - 始终使用 PBKDF2（新格式）"""
    # 生成随机盐值
    salt = secrets.token_bytes(32)
    
    # 使用 PBKDF2 生成哈希
    hash_value = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000  # 迭代次数
    )
    
    # 格式：algorithm$salt_base64$hash_base64
    salt_b64 = base64.b64encode(salt).decode('utf-8')
    hash_b64 = base64.b64encode(hash_value).decode('utf-8')
    
    return f"pbkdf2_sha256${salt_b64}${hash_b64}"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    from datetime import datetime
    import sys
    
    to_encode = data.copy()
    
    # Python 3.7 兼容性：使用 utcnow() 而不是 now(timezone.utc)
    if sys.version_info >= (3, 11):
        from datetime import timezone
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    else:
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_session():
    with Session(engine) as session:
        yield session

async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception
    return user
