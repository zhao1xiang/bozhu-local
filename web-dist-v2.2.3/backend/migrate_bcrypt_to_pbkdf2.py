#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
密码格式迁移工具 - bcrypt 转 PBKDF2
用于将客户的旧数据库（bcrypt 格式）转换为新格式（PBKDF2）
"""

import sys
import os
import shutil
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import Session, select
from database import engine
from models.user import User
from security import get_password_hash

def migrate_passwords():
    """迁移密码格式"""
    
    print()
    print("=" * 70)
    print("密码格式迁移工具 - bcrypt 转 PBKDF2")
    print("=" * 70)
    print()
    print("⚠️  重要提示：")
    print("   - 此工具会修改数据库中的密码格式")
    print("   - 迁移前会自动备份数据库")
    print("   - 迁移后需要用户重新设置密码")
    print()
    
    # 检查数据库文件
    db_file = "database.db"
    if not os.path.exists(db_file):
        print(f"✗ 错误：未找到数据库文件 {db_file}")
        return False
    
    # 备份数据库
    backup_file = f"database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    print(f"[1/4] 备份数据库...")
    try:
        shutil.copy2(db_file, backup_file)
        print(f"   ✓ 已备份到: {backup_file}")
    except Exception as e:
        print(f"   ✗ 备份失败: {e}")
        return False
    
    print()
    
    # 扫描用户
    print(f"[2/4] 扫描用户...")
    try:
        with Session(engine) as session:
            users = session.exec(select(User)).all()
            
            if not users:
                print("   ⚠ 数据库中没有用户")
                return True
            
            print(f"   找到 {len(users)} 个用户")
            print()
            
            bcrypt_users = []
            pbkdf2_users = []
            unknown_users = []
            
            for user in users:
                if user.hashed_password.startswith('$2b$') or user.hashed_password.startswith('$2a$'):
                    bcrypt_users.append(user)
                elif user.hashed_password.startswith('pbkdf2_sha256$'):
                    pbkdf2_users.append(user)
                else:
                    unknown_users.append(user)
            
            print(f"   - bcrypt 格式: {len(bcrypt_users)} 个")
            print(f"   - PBKDF2 格式: {len(pbkdf2_users)} 个")
            if unknown_users:
                print(f"   - 未知格式: {len(unknown_users)} 个")
            
            print()
            
            if not bcrypt_users:
                print("   ✓ 没有需要迁移的用户")
                return True
            
    except Exception as e:
        print(f"   ✗ 扫描失败: {e}")
        return False
    
    # 显示需要迁移的用户
    print(f"[3/4] 需要迁移的用户:")
    print()
    for i, user in enumerate(bcrypt_users, 1):
        print(f"   {i}. {user.username} (角色: {user.role})")
    print()
    
    # 确认迁移
    print("⚠️  迁移说明：")
    print("   - bcrypt 格式的密码无法直接转换")
    print("   - 需要为这些用户设置新密码")
    print("   - 建议使用默认密码，让用户首次登录后修改")
    print()
    
    default_password = input("请输入默认密码（留空使用 'admin123'）: ").strip()
    if not default_password:
        default_password = "admin123"
    
    print()
    confirm = input(f"确认为 {len(bcrypt_users)} 个用户设置密码为 '{default_password}'? (y/n): ")
    
    if confirm.lower() != 'y':
        print()
        print("✗ 已取消迁移")
        return False
    
    print()
    
    # 执行迁移
    print(f"[4/4] 执行迁移...")
    try:
        new_hash = get_password_hash(default_password)
        
        with Session(engine) as session:
            success_count = 0
            
            for user in bcrypt_users:
                try:
                    # 重新查询用户（确保是最新的）
                    db_user = session.exec(select(User).where(User.id == user.id)).first()
                    if db_user:
                        db_user.hashed_password = new_hash
                        session.add(db_user)
                        success_count += 1
                        print(f"   ✓ {db_user.username}")
                except Exception as e:
                    print(f"   ✗ {user.username}: {e}")
            
            session.commit()
            
            print()
            print(f"   成功迁移: {success_count}/{len(bcrypt_users)} 个用户")
    
    except Exception as e:
        print(f"   ✗ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("=" * 70)
    print("✓ 迁移完成")
    print("=" * 70)
    print()
    print("迁移结果：")
    print(f"  - 已迁移用户: {success_count} 个")
    print(f"  - 新密码: {default_password}")
    print(f"  - 备份文件: {backup_file}")
    print()
    print("下一步：")
    print("  1. 通知用户使用新密码登录")
    print("  2. 建议用户首次登录后修改密码")
    print("  3. 如果迁移有问题，可以恢复备份文件")
    print()
    
    return True

def main():
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "密码格式迁移工具" + " " * 30 + "║")
    print("╚" + "=" * 68 + "╝")
    
    try:
        success = migrate_passwords()
        return 0 if success else 1
    except KeyboardInterrupt:
        print()
        print()
        print("✗ 用户取消操作")
        return 1
    except Exception as e:
        print()
        print(f"✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
