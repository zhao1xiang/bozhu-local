from sqlmodel import Session, select, text
from database import engine, create_db_and_tables
from models.user import User
from security import get_password_hash
import os

def check_admin():
    print("=== 检查管理员用户 ===")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"数据库文件路径: database.db")
    print(f"数据库文件是否存在: {os.path.exists('database.db')}")
    
    # 1. 重新创建表结构
    print("\n1. 创建数据库表结构...")
    try:
        create_db_and_tables()
        print("[OK] 数据库表结构创建成功")
    except Exception as e:
        print(f"[ERROR] 创建表结构失败: {e}")
        return
    
    # 2. 创建或重置管理员用户
    print("\n2. 检查管理员用户...")
    with Session(engine) as session:
        try:
            user = session.exec(select(User).where(User.username == "admin")).first()
            if user:
                print(f"[INFO] 管理员用户已存在. ID: {user.id}")
                # 重置密码
                user.hashed_password = get_password_hash("admin")
                session.add(user)
                session.commit()
                print("[OK] 管理员密码重置为 'admin'")
            else:
                print("[INFO] 管理员用户不存在，创建中...")
                admin_user = User(username="admin", hashed_password=get_password_hash("admin"))
                session.add(admin_user)
                session.commit()
                print("[OK] 管理员用户创建成功，密码: 'admin'")
        except Exception as e:
            print(f"[ERROR] 操作数据库失败: {e}")
            return
    
    print("\n=== 检查完成 ===")
    print("管理员用户状态: 就绪")
    print("登录凭据: 用户名: admin, 密码: admin")

if __name__ == "__main__":
    check_admin()
