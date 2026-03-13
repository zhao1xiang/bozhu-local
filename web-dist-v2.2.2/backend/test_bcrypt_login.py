#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 bcrypt 格式登录
验证 Web 版本是否能正确验证 EXE 版本的密码
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_login():
    """测试登录功能"""
    
    print()
    print("=" * 60)
    print("测试 bcrypt 格式登录（EXE 版本兼容性）")
    print("=" * 60)
    print()
    
    try:
        from sqlmodel import Session, select
        from database import engine, create_db_and_tables
        from models.user import User
        from security import verify_password, get_password_hash
        
        # 1. 确保数据库表存在
        print("1. 初始化数据库...")
        create_db_and_tables()
        print("   ✓ 数据库表已创建")
        print()
        
        # 2. 创建或更新 admin 用户（使用 bcrypt 格式）
        print("2. 创建/更新 admin 用户（bcrypt 格式）...")
        
        try:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            bcrypt_hash = pwd_context.hash("admin")
            print(f"   生成的 bcrypt 哈希: {bcrypt_hash[:50]}...")
            
            with Session(engine) as session:
                user = session.exec(select(User).where(User.username == "admin")).first()
                
                if user:
                    print("   用户已存在，更新密码为 bcrypt 格式...")
                    user.hashed_password = bcrypt_hash
                    session.add(user)
                else:
                    print("   创建新用户...")
                    user = User(
                        username="admin",
                        hashed_password=bcrypt_hash,
                        role="admin",
                        full_name="系统管理员"
                    )
                    session.add(user)
                
                session.commit()
                print("   ✓ admin 用户已准备（密码：admin）")
            
        except ImportError:
            print("   ✗ 错误：缺少 passlib 或 bcrypt 库")
            print("   请运行: pip install passlib[bcrypt] bcrypt")
            return False
        
        print()
        
        # 3. 测试密码验证
        print("3. 测试密码验证...")
        
        with Session(engine) as session:
            user = session.exec(select(User).where(User.username == "admin")).first()
            
            if not user:
                print("   ✗ 用户不存在")
                return False
            
            # 检测密码格式
            if user.hashed_password.startswith('$2b$') or user.hashed_password.startswith('$2a$'):
                print("   密码格式: bcrypt（EXE 版本）✓")
            elif user.hashed_password.startswith('pbkdf2_sha256$'):
                print("   密码格式: PBKDF2（Web 版本）")
            else:
                print("   密码格式: 未知")
            
            print()
            
            # 测试正确密码
            print("   测试正确密码 'admin'...")
            if verify_password("admin", user.hashed_password):
                print("   ✓ 密码验证成功")
            else:
                print("   ✗ 密码验证失败")
                return False
            
            # 测试错误密码
            print("   测试错误密码 'wrongpassword'...")
            if not verify_password("wrongpassword", user.hashed_password):
                print("   ✓ 错误密码正确拒绝")
            else:
                print("   ✗ 错误密码验证通过（不应该）")
                return False
        
        print()
        print("=" * 60)
        print("✓ 所有测试通过")
        print("=" * 60)
        print()
        print("结论：")
        print("  • Web 版本可以正确验证 bcrypt 格式密码")
        print("  • 完全兼容 EXE 版本的数据库")
        print("  • 可以使用 admin/admin 登录")
        print()
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print()
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "bcrypt 登录测试工具" + " " * 16 + "║")
    print("╚" + "=" * 58 + "╝")
    
    success = test_login()
    
    if success:
        print("提示：")
        print("  1. 现在可以启动 Web 服务器")
        print("  2. 使用 admin/admin 登录")
        print("  3. 这模拟了 EXE 版本的数据库")
        return 0
    else:
        print("提示：")
        print("  1. 检查是否安装了 passlib 和 bcrypt")
        print("  2. 运行: pip install passlib[bcrypt] bcrypt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
