"""
迁移脚本：将数据库中的 bcrypt 密码哈希转换为 pbkdf2_sha256
"""
import sys
import os
from sqlmodel import Session, select
from database import engine
from models.user import User
from security import get_password_hash

def migrate_passwords():
    """迁移所有用户的密码哈希"""
    print("=" * 50)
    print("密码哈希迁移工具")
    print("=" * 50)
    print()
    
    with Session(engine) as session:
        # 获取所有用户
        users = session.exec(select(User)).all()
        
        if not users:
            print("❌ 数据库中没有用户")
            return
        
        print(f"找到 {len(users)} 个用户")
        print()
        
        # 对于每个用户，如果密码哈希是 bcrypt 格式，则重置为默认密码
        updated_count = 0
        for user in users:
            # 检查是否是 bcrypt 格式（以 $2b$ 开头）
            if user.hashed_password.startswith('$2b$') or user.hashed_password.startswith('$2a$'):
                print(f"用户 '{user.username}' 使用旧的 bcrypt 格式")
                
                # 重置为默认密码 "admin123"
                default_password = "admin123"
                new_hash = get_password_hash(default_password)
                user.hashed_password = new_hash
                session.add(user)
                updated_count += 1
                
                print(f"  ✓ 已重置为默认密码: {default_password}")
                print()
        
        if updated_count > 0:
            session.commit()
            print("=" * 50)
            print(f"✓ 成功更新 {updated_count} 个用户的密码")
            print("=" * 50)
            print()
            print("重要提示：")
            print(f"  所有用户的密码已重置为: admin123")
            print("  请在首次登录后立即修改密码")
        else:
            print("=" * 50)
            print("✓ 所有用户已使用新的密码格式，无需迁移")
            print("=" * 50)

if __name__ == "__main__":
    try:
        migrate_passwords()
    except Exception as e:
        print()
        print("=" * 50)
        print("❌ 迁移失败")
        print("=" * 50)
        print()
        print(f"错误信息: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
