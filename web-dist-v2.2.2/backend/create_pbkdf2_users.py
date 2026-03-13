#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建 PBKDF2 格式的测试用户
由于打包后 bcrypt 不可用，所有账号都使用 PBKDF2 格式
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import Session, select
from database import engine, create_db_and_tables
from models.user import User
from security import get_password_hash

def create_users():
    """创建测试用户 - 全部使用 PBKDF2 格式"""
    
    print()
    print("=" * 60)
    print("创建测试用户 - PBKDF2 格式（打包兼容）")
    print("=" * 60)
    print()
    
    # 初始化数据库
    create_db_and_tables()
    
    # 生成 PBKDF2 格式密码
    pbkdf2_hash_admin = get_password_hash("admin")
    pbkdf2_hash_admin123 = get_password_hash("admin123")
    
    with Session(engine) as session:
        # 1. admin 用户 - 密码 admin
        user1 = session.exec(select(User).where(User.username == "admin")).first()
        if user1:
            user1.hashed_password = pbkdf2_hash_admin
            session.add(user1)
            print("✓ 更新 admin 用户")
        else:
            user1 = User(
                username="admin",
                hashed_password=pbkdf2_hash_admin,
                role="admin",
                full_name="系统管理员"
            )
            session.add(user1)
            print("✓ 创建 admin 用户")
        
        print(f"  用户名: admin")
        print(f"  密码: admin")
        print(f"  格式: PBKDF2")
        print()
        
        # 2. admin2 用户 - 密码 admin123
        user2 = session.exec(select(User).where(User.username == "admin2")).first()
        if user2:
            user2.hashed_password = pbkdf2_hash_admin123
            session.add(user2)
            print("✓ 更新 admin2 用户")
        else:
            user2 = User(
                username="admin2",
                hashed_password=pbkdf2_hash_admin123,
                role="admin",
                full_name="管理员2"
            )
            session.add(user2)
            print("✓ 创建 admin2 用户")
        
        print(f"  用户名: admin2")
        print(f"  密码: admin123")
        print(f"  格式: PBKDF2")
        print()
        
        # 删除 admin3 和 admin4（如果存在）
        for username in ["admin3", "admin4"]:
            user = session.exec(select(User).where(User.username == username)).first()
            if user:
                session.delete(user)
                print(f"✓ 删除 {username} 用户（不再需要）")
        
        session.commit()
        
    print()
    print("=" * 60)
    print("✓ 所有用户创建完成")
    print("=" * 60)
    print()
    print("测试账号列表（全部 PBKDF2 格式）：")
    print()
    print("  1. admin / admin")
    print("  2. admin2 / admin123")
    print()
    print("说明：")
    print("  - 所有账号都使用 PBKDF2 格式")
    print("  - 打包后无需 bcrypt 库")
    print("  - 完全兼容 Windows 7")
    print()
    
    return True

def main():
    print()
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "创建 PBKDF2 格式用户工具" + " " * 13 + "║")
    print("╚" + "=" * 58 + "╝")
    
    success = create_users()
    
    if success:
        print("提示：")
        print("  1. 现在可以启动 Web 服务器")
        print("  2. 使用 admin/admin 或 admin2/admin123 登录")
        print("  3. 打包后无需 bcrypt 库支持")
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
