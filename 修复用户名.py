import sqlite3
import bcrypt

# 连接数据库
conn = sqlite3.connect('dist-package/backend/database.db')
cursor = conn.cursor()

print("=" * 60)
print("修复用户名")
print("=" * 60)
print()

# 查看当前用户
print("当前用户列表：")
cursor.execute("SELECT id, username FROM user")
users = cursor.fetchall()
for user in users:
    print(f"  ID: {user[0]}, 用户名: {user[1]}")
print()

# 修复 admin 用户名
print("修复 admin 用户名...")
cursor.execute("UPDATE user SET username = 'admin' WHERE id = 1")
conn.commit()
print("✓ 已修复")
print()

# 确认修复
print("修复后的用户列表：")
cursor.execute("SELECT id, username FROM user")
users = cursor.fetchall()
for user in users:
    print(f"  ID: {user[0]}, 用户名: {user[1]}")
print()

# 重置 admin 密码为 admin
print("重置 admin 密码为 'admin'...")
hashed = bcrypt.hashpw("admin".encode('utf-8'), bcrypt.gensalt())
cursor.execute("UPDATE user SET hashed_password = ? WHERE username = 'admin'", (hashed.decode('utf-8'),))
conn.commit()
print("✓ admin 密码已重置为 'admin'")
print()

# 重置 admin666 密码为 admin666
print("重置 admin666 密码为 'admin666'...")
hashed = bcrypt.hashpw("admin666".encode('utf-8'), bcrypt.gensalt())
cursor.execute("UPDATE user SET hashed_password = ? WHERE username = 'admin666'", (hashed.decode('utf-8'),))
conn.commit()
print("✓ admin666 密码已重置为 'admin666'")
print()

conn.close()

print("=" * 60)
print("修复完成！")
print("=" * 60)
print()
print("现在可以使用以下账号登录：")
print("  1. admin / admin")
print("  2. admin666 / admin666")
print()
