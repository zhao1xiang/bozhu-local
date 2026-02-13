import sqlite3
import os

print("=" * 60)
print("诊断数据库路径问题")
print("=" * 60)
print()

# 检查 dist-package/backend 目录下的数据库
db_path = "dist-package/backend/database.db"
print(f"[1] 检查磁盘数据库: {db_path}")
print(f"    文件存在: {os.path.exists(db_path)}")
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM patient")
    count = cursor.fetchone()[0]
    print(f"    患者数量: {count}")
    conn.close()
print()

# 检查 backend 目录下的数据库（开发环境）
dev_db_path = "backend/database.db"
print(f"[2] 检查开发数据库: {dev_db_path}")
print(f"    文件存在: {os.path.exists(dev_db_path)}")
if os.path.exists(dev_db_path):
    conn = sqlite3.connect(dev_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM patient")
    count = cursor.fetchone()[0]
    print(f"    患者数量: {count}")
    conn.close()
print()

# 检查 backend/dist 目录下的数据库
dist_db_path = "backend/dist/database.db"
print(f"[3] 检查 dist 数据库: {dist_db_path}")
print(f"    文件存在: {os.path.exists(dist_db_path)}")
if os.path.exists(dist_db_path):
    conn = sqlite3.connect(dist_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM patient")
    count = cursor.fetchone()[0]
    print(f"    患者数量: {count}")
    
    # 显示一些患者信息
    cursor.execute("SELECT id, name FROM patient LIMIT 5")
    patients = cursor.fetchall()
    print(f"    前5个患者:")
    for p in patients:
        print(f"      - ID: {p[0]}, 姓名: {p[1]}")
    conn.close()
print()

print("=" * 60)
print("结论")
print("=" * 60)
print()
print("如果 backend/dist/database.db 有数据，")
print("说明 PyInstaller 在打包时把这个数据库文件打包进去了。")
print()
print("解决方案：")
print("1. 清空 backend/dist/database.db")
print("2. 重新打包后端")
print("3. 复制到 dist-package")
print()
