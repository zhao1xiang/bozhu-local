#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试 bcrypt 和密码验证"""

from passlib.context import CryptContext
from sqlmodel import Session, select
from database import engine
from models.user import User

# 创建密码上下文
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__default_rounds=12,
    bcrypt__default_ident="2b"
)

print("=" * 60)
print("测试 bcrypt 密码哈希和验证")
print("=" * 60)

# 测试密码哈希
test_password = "admin"
print(f"\n1. 测试密码: {test_password}")

try:
    hashed = pwd_context.hash(test_password)
    print(f"   哈希成功: {hashed[:50]}...")
    
    # 测试验证
    is_valid = pwd_context.verify(test_password, hashed)
    print(f"   验证结果: {'✅ 成功' if is_valid else '❌ 失败'}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 检查数据库中的 admin 用户
print(f"\n2. 检查数据库中的 admin 用户")
try:
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == "admin")).first()
        if user:
            print(f"   用户名: {user.username}")
            print(f"   密码哈希: {user.hashed_password[:50]}...")
            
            # 测试验证数据库中的密码
            is_valid = pwd_context.verify("admin", user.hashed_password)
            print(f"   验证 'admin' 密码: {'✅ 成功' if is_valid else '❌ 失败'}")
            
            if not is_valid:
                print(f"\n3. 重置 admin 密码")
                user.hashed_password = pwd_context.hash("admin")
                session.add(user)
                session.commit()
                print(f"   ✅ 密码已重置")
                
                # 再次验证
                is_valid = pwd_context.verify("admin", user.hashed_password)
                print(f"   重新验证: {'✅ 成功' if is_valid else '❌ 失败'}")
        else:
            print("   ❌ 未找到 admin 用户")
except Exception as e:
    print(f"   ❌ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
