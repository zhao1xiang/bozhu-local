"""
更新或添加用户
"""
import sqlite3
import sys
sys.path.insert(0, 'backend')

from passlib.context import CryptContext

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 连接数据库
db_path = 'dist-package/backend/database.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("用户管理工具")
print("=" * 60)
print()

# 显示现有用户
cursor.execute('SELECT id, username FROM user')
users = cursor.fetchall()
print("现有用户:")
for u in users:
    print(f"  ID: {u[0]}, 用户名: {u[1]}")
print()

# 获取用户输入
username = input("请输入用户名: ").strip()
if not username:
    print("用户名不能为空")
    sys.exit(1)

password = input("请输入密码: ").strip()
if not password:
    print("密码不能为空")
    sys.exit(1)

# 检查用户是否存在
cursor.execute('SELECT id FROM user WHERE username = ?', (username,))
existing_user = cursor.fetchone()

# 生成密码哈希
hashed_password = pwd_context.hash(password)

if existing_user:
    # 更新密码
    cursor.execute('UPDATE user SET hashed_password = ? WHERE username = ?', 
                   (hashed_password, username))
    print(f"\n✓ 已更新用户 '{username}' 的密码")
else:
    # 添加新用户
    cursor.execute('INSERT INTO user (username, hashed_password) VALUES (?, ?)',
                   (username, hashed_password))
    print(f"\n✓ 已添加新用户 '{username}'")

conn.commit()
conn.close()

print("\n完成！请重启应用后使用新密码登录。")
print()
input("按回车键退出...")
