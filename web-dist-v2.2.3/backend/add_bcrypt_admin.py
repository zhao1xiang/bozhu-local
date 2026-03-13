#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加 bcrypt 格式的 admin 账号
用于测试 EXE 版本数据库兼容性
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import Session, select
from database import engine
from models.user import User

def add_bcrypt_admin():
    """添加使用 bcrypt 格式密码的 admin 账号"""
    
    print("=" * 60)
    print("添加 bcrypt 格式的 admin 账号（模拟 EXE 版本）")
    print("=" * 60)
    print()
    
    try:
        # 生成 bcrypt 格式的密码哈希
        # 密码：admin
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        bcrypt_hash = pwd_context.hash("admin")
        
        print(f"生成的 bcrypt 哈希: {bcrypt_hash}")
        print()
        
        with Session(engine) as session:
            # 检查是否已存在 admin 用户
            existing_admin = session.exec(
                select(User).where(User.username == "admin")
            ).first()
            
            if existing_admin:
                print(f"⚠ 用户 'admin' 已存在")
                print(f"  当前密码格式: ", end="")
                
                if existing_admin.hashed_password.startswith('$2b$') or existing_admin.hashed_password.startswith('$2a$'):
                    print("bcrypt（EXE 版本）")
                elif existing_admin.hashed_password.startswith('pbkdf2_sha256$'):
                    print("PBKDF2（Web 版本）")
                else:
                    print("未知")
                
                print()
                response = input("是否更新为 bcrypt 格式？(y/n): ")
                
                if response.lower() == 'y':
                    existing_admin.hashed_password = bcrypt_hash
                    session.add(existing_admin)
                    session.commit()
                    print("✓ 已更新 admin 用户密码为 bcrypt 格式")
                else:
                    print("✗ 取消更新")
                    return False
            else:
                # 创建新的 admin 用户
                new_admin = User(
                    username="admin",
                    hashed_password=bcrypt_hash,
                    role="admin",
                    full_name="系统管理员"
                )
                session.add(new_admin)
                session.commit()
                print("✓ 已创建 admin 用户（bcrypt 格式）")
            
            print()
            print("账号信息：")
            print("  用户名: admin")
            print("  密码: admin")
            print("  角色: admin")
            print("  密码格式: bcrypt（EXE 版本格式）")
            print()
            
            # 验证密码
            print("验证密码...")
            from security import verify_password
            
            if verify_password("admin", bcrypt_hash):
                print("✓ 密码验证成功")
            else:
                print("✗ 密码验证失败")
                return False
            
            print()
            print("=" * 60)
            print("✓ 完成！现在可以使用 admin/admin 登录")
            print("=" * 60)
            
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
    print("║" + " " * 10 + "添加 bcrypt 格式 admin 账号工具" + " " * 10 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    success = add_bcrypt_admin()
    
    if success:
        print()
        print("提示：")
        print("  1. 此账号使用 bcrypt 格式（模拟 EXE 版本）")
        print("  2. 可用于测试 Web 版本的兼容性")
        print("  3. 登录后可以修改密码（会自动升级为 PBKDF2 格式）")
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
