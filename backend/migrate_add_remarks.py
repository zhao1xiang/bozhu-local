"""
数据库迁移脚本：添加患者备注字段
版本：v2.2.2
日期：2026-03-11
"""
import sqlite3
import shutil
from datetime import datetime
import os

def backup_database(db_path):
    """备份数据库"""
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return False
    
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✓ 数据库已备份: {backup_path}")
        return True
    except Exception as e:
        print(f"✗ 数据库备份失败: {e}")
        return False

def column_exists(cursor, table_name, column_name):
    """检查列是否存在"""
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        return column_name in columns
    except Exception as e:
        print(f"✗ 检查列失败 {table_name}.{column_name}: {e}")
        return False

def add_column(cursor, table_name, column_name, column_type, description=""):
    """安全地添加列（如果不存在）"""
    if column_exists(cursor, table_name, column_name):
        print(f"  - 字段已存在，跳过: {table_name}.{column_name}")
        return False
    
    try:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
        print(f"✓ 添加字段: {table_name}.{column_name} ({description})")
        return True
    except Exception as e:
        print(f"✗ 添加字段失败 {table_name}.{column_name}: {e}")
        return False

def migrate():
    """执行迁移"""
    db_path = "database.db"
    
    print("=" * 60)
    print("数据库迁移：添加患者备注字段")
    print("=" * 60)
    print()
    
    # 检查数据库文件
    if not os.path.exists(db_path):
        print(f"✗ 数据库文件不存在: {db_path}")
        return False
    
    # 备份数据库
    print("[1/3] 备份数据库...")
    if not backup_database(db_path):
        print("⚠ 备份失败，但继续执行迁移...")
    print()
    
    # 连接数据库
    print("[2/3] 连接数据库...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("✓ 数据库连接成功")
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return False
    print()
    
    # 执行迁移
    print("[3/3] 执行迁移...")
    changes_made = 0
    
    try:
        # 添加备注字段
        if add_column(cursor, 'patient', 'remarks', 'TEXT', '备注'):
            changes_made += 1
        
        # 提交更改
        conn.commit()
        print()
        
        # 验证迁移
        print("验证迁移结果...")
        if column_exists(cursor, 'patient', 'remarks'):
            print("✓ 验证成功: patient.remarks 字段已添加")
        else:
            print("✗ 验证失败: patient.remarks 字段不存在")
            conn.close()
            return False
        
        print()
        print("=" * 60)
        print(f"✓ 迁移完成! 新增 {changes_made} 个字段")
        print("=" * 60)
        
        conn.close()
        return True
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ 迁移失败: {e}")
        print("=" * 60)
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        return False

if __name__ == "__main__":
    success = migrate()
    if success:
        print("\n迁移成功！可以启动服务器了。")
    else:
        print("\n迁移失败！请检查错误信息。")
    
    input("\n按回车键退出...")
