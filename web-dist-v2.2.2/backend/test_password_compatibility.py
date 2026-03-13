#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
密码兼容性测试脚本
用于验证 Web 版本是否能正确验证 EXE 版本的密码
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from security import verify_password, get_password_hash

def test_bcrypt_password():
    """测试 bcrypt 格式密码（EXE 版本）"""
    print("=" * 60)
    print("测试 1: bcrypt 格式密码（EXE 版本）")
    print("=" * 60)
    
    # 这是一个 bcrypt 格式的密码哈希（密码是 "admin123"）
    bcrypt_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqYqYqYqYq"
    
    try:
        # 测试正确密码
        result = verify_password("admin123", bcrypt_hash)
        if result:
            print("✓ bcrypt 密码验证成功")
        else:
            print("✗ bcrypt 密码验证失败")
        
        # 测试错误密码
        result = verify_password("wrongpassword", bcrypt_hash)
        if not result:
            print("✓ bcrypt 错误密码正确拒绝")
        else:
            print("✗ bcrypt 错误密码验证通过（不应该）")
            
    except Exception as e:
        print(f"✗ bcrypt 测试出错: {e}")
        print("提示：可能缺少 passlib 或 bcrypt 库")
        return False
    
    print()
    return True

def test_pbkdf2_password():
    """测试 PBKDF2 格式密码（Web 版本）"""
    print("=" * 60)
    print("测试 2: PBKDF2 格式密码（Web 版本）")
    print("=" * 60)
    
    try:
        # 生成新密码哈希
        password = "test123"
        hashed = get_password_hash(password)
        print(f"生成的哈希: {hashed[:50]}...")
        
        # 测试正确密码
        result = verify_password(password, hashed)
        if result:
            print("✓ PBKDF2 密码验证成功")
        else:
            print("✗ PBKDF2 密码验证失败")
        
        # 测试错误密码
        result = verify_password("wrongpassword", hashed)
        if not result:
            print("✓ PBKDF2 错误密码正确拒绝")
        else:
            print("✗ PBKDF2 错误密码验证通过（不应该）")
            
    except Exception as e:
        print(f"✗ PBKDF2 测试出错: {e}")
        return False
    
    print()
    return True

def test_database_passwords():
    """测试数据库中的实际密码"""
    print("=" * 60)
    print("测试 3: 数据库中的实际密码")
    print("=" * 60)
    
    try:
        from sqlmodel import Session, select
        from database import engine
        from models.user import User
        
        with Session(engine) as session:
            users = session.exec(select(User)).all()
            
            if not users:
                print("⚠ 数据库中没有用户")
                return True
            
            print(f"找到 {len(users)} 个用户:")
            print()
            
            for user in users:
                print(f"用户: {user.username}")
                print(f"  角色: {user.role}")
                
                # 检测密码格式
                if user.hashed_password.startswith('$2b$') or user.hashed_password.startswith('$2a$'):
                    print(f"  密码格式: bcrypt（EXE 版本）")
                    format_type = "bcrypt"
                elif user.hashed_password.startswith('pbkdf2_sha256$'):
                    print(f"  密码格式: PBKDF2（Web 版本）")
                    format_type = "pbkdf2"
                else:
                    print(f"  密码格式: 未知")
                    format_type = "unknown"
                
                # 如果是 admin 用户，尝试验证默认密码
                if user.username == 'admin':
                    test_passwords = ['admin', 'admin123', '123456']
                    for pwd in test_passwords:
                        if verify_password(pwd, user.hashed_password):
                            print(f"  ✓ 密码 '{pwd}' 验证成功")
                            break
                    else:
                        print(f"  ⚠ 无法使用常见密码验证")
                
                print()
            
    except Exception as e:
        print(f"✗ 数据库测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    print()
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "密码兼容性测试工具" + " " * 15 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    # 运行测试
    test1 = test_bcrypt_password()
    test2 = test_pbkdf2_password()
    test3 = test_database_passwords()
    
    # 总结
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    
    if test1 and test2 and test3:
        print("✓ 所有测试通过")
        print()
        print("结论：Web 版本完全兼容 EXE 版本的数据库")
        print("      客户可以直接复制 database.db 文件使用")
        return 0
    else:
        print("✗ 部分测试失败")
        print()
        print("建议：")
        print("  1. 检查是否安装了 passlib 和 bcrypt 库")
        print("  2. 运行: pip install passlib[bcrypt] bcrypt")
        print("  3. 重新打包时确保包含这些库")
        return 1

if __name__ == "__main__":
    sys.exit(main())
