"""
测试 admin666 账号登录
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
print("测试 admin666 账号")
print("=" * 60)
print()

# 查询用户
cursor.execute('SELECT id, username, hashed_password FROM user WHERE username = ?', ('admin666',))
user = cursor.fetchone()

if user:
    user_id, username, hashed_password = user
    print(f"✓ 用户存在")
    print(f"  ID: {user_id}")
    print(f"  用户名: {username}")
    print(f"  密码哈希: {hashed_password[:30]}...")
    print()
    
    # 测试密码验证
    test_passwords = ['admin666', 'admin123', '123456', 'password']
    print("测试密码验证:")
    for pwd in test_passwords:
        try:
            result = pwd_context.verify(pwd, hashed_password)
            if result:
                print(f"  ✓ 密码 '{pwd}' 验证成功")
            else:
                print(f"  ✗ 密码 '{pwd}' 验证失败")
        except Exception as e:
            print(f"  ✗ 密码 '{pwd}' 验证出错: {e}")
    
    print()
    print("请输入你设置的密码进行测试:")
    user_input = input("密码: ")
    if user_input:
        try:
            result = pwd_context.verify(user_input, hashed_password)
            if result:
                print(f"✓ 密码正确！")
            else:
                print(f"✗ 密码错误")
        except Exception as e:
            print(f"✗ 验证出错: {e}")
else:
    print("✗ 用户不存在")

print()
print("=" * 60)
print("所有用户列表:")
print("=" * 60)
cursor.execute('SELECT id, username FROM user')
users = cursor.fetchall()
for u in users:
    print(f"  ID: {u[0]}, 用户名: {u[1]}")

conn.close()
