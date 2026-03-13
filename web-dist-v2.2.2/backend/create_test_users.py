#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试用户 - 同时支持 bcrypt 和 PBKDF2 格式
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import Session, select
from database import engine, create_db_and_tables
from models.user import User
from security import get_password_hash

def create_test_users():
    """创建测试用户"""
    
    print()
    print("=" * 60)
    print("创建测试用户 - 验证密码兼容性")
    print("=" * 60)
    print()
    
    # 初始化数据库
    create_db_and_tables()
    
    try:
        # 生成 bcrypt 格式密码
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        bcrypt_hash_admin = pwd_context.hash("admin")
        bcrypt_hash_admin123 = pwd_context.hash("admin123")
        
        # 生成 PBKDF2 格式密码
        pbkdf2_hash_admin = get_password_hash("admin")
        pbkdf2_hash_admin123 = get_password_hash("admin123")
        
        with Session(engine) as session:
            # 1. admin 用户 - bcrypt 格式，密码 admin
            user1 = session.exec(select(User).where(User.username == "admin")).first()
            if user1:
                user1.hashed_password = bcrypt_hash_admin
                session.add(user1)
                print("✓ 更新 admin 用户")
            else:
                user1 = User(
                    username="admin",
                    hashed_password=bcrypt_hash_admin,
                    role="admin",
                    full_name="系统管理员"
                )
                session.add(user1)
                print("✓ 创建 admin 用户")
            
            print(f"  用户名: admin")
            print(f"  密码: admin")
            print(f"  格式: bcrypt（EXE 版本格式）")
            print()
            
            # 2. admin2 用户 - bcrypt 格式，密码 admin123
            user2 = session.exec(select(User).where(User.username == "admin2")).first()
            if user2:
                user2.hashed_password = bcrypt_hash_admin123
                session.add(user2)
                print("✓ 更新 admin2 用户")
            else:
                user2 = User(
                    username="admin2",
                    hashed_password=bcrypt_hash_admin123,
                    role="admin",
                    full_name="管理员2（bcrypt）"
                )
                session.add(user2)
                print("✓ 创建 admin2 用户")
            
            print(f"  用户名: admin2")
            print(f"  密码: admin123")
            print(f"  格式: bcrypt（EXE 版本格式）")
            print()
            
            # 3. admin3 用户 - PBKDF2 格式，密码 admin
            user3 = session.exec(select(User).where(User.username == "admin3")).first()
            if user3:
                user3.hashed_password = pbkdf2_hash_admin
                session.add(user3)
                print("✓ 更新 admin3 用户")
            else:
                user3 = User(
                    username="admin3",
                    hashed_password=pbkdf2_hash_admin,
                    role="admin",
                    full_name="管理员3（PBKDF2）"
                )
                session.add(user3)
                print("✓ 创建 admin3 用户")
            
            print(f"  用户名: admin3")
            print(f"  密码: admin")
            print(f"  格式: PBKDF2（Web 版本格式）")
            print()
            
            # 4. admin4 用户 - PBKDF2 格式，密码 admin123
            user4 = session.exec(select(User).where(User.username == "admin4")).first()
            if user4:
                user4.hashed_password = pbkdf2_hash_admin123
                session.add(user4)
                print("✓ 更新 admin4 用户")
            else:
                user4 = User(
                    username="admin4",
                    hashed_password=pbkdf2_hash_admin123,
                    role="admin",
                    full_name="管理员4（PBKDF2）"
                )
                session.add(user4)
                print("✓ 创建 admin4 用户")
            
            print(f"  用户名: admin4")
            print(f"  密码: admin123")
            print(f"  格式: PBKDF2（Web 版本格式）")
            print()
            
            session.commit()
            
        print("=" * 60)
        print("✓ 所有测试用户创建完成")
        print("=" * 60)
        print()
        print("测试账号列表：")
        print()
        print("bcrypt 格式（模拟 EXE 版本）：")
        print("  1. admin / admin")
        print("  2. admin2 / admin123")
        print()
        print("PBKDF2 格式（Web 版本）：")
        print("  3. admin3 / admin")
        print("  4. admin4 / admin123")
        print()
        print("所有账号都应该能正常登录！")
        print()
        
        return True
        
    except ImportError as e:
        print(f"✗ 错误：缺少必要的库")
        print(f"  {e}")
        print()
        print("请安装 passlib 和 bcrypt：")
        print("  pip install passlib[bcrypt] bcrypt")
        return False
        
    except Exception as e:
        print(f"✗ 错误：{e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print()
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "创建测试用户工具" + " " * 18 + "║")
    print("╚" + "=" * 58 + "╝")
    
    success = create_test_users()
    
    if success:
        print("提示：")
        print("  1. 现在可以启动 Web 服务器")
        print("  2. 使用任意测试账号登录")
        print("  3. 验证两种密码格式都能正常工作")
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
