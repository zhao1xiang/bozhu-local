import sys
sys.path.insert(0, 'backend')
from sqlmodel import Session, select, create_engine
from models.user import User

engine = create_engine('sqlite:///simple-web-package-win7-v2.1.7/database.db')
session = Session(engine)
users = session.exec(select(User)).all()

print()
print("=" * 60)
print("数据库中的用户列表")
print("=" * 60)
print()

for i, u in enumerate(users, 1):
    pwd_format = "bcrypt" if u.hashed_password.startswith("$2b$") else "PBKDF2"
    print(f"{i}. {u.username:10} - 密码格式: {pwd_format}")

print()
print(f"总计: {len(users)} 个用户")
print()
