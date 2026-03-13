"""
数据库迁移脚本 - 添加新字段
用于在客户现有数据库上添加新字段，不会丢失现有数据

新增字段：
患者表(patient):
  - medical_card_number: 就诊卡号

预约表(appointment):
  - attending_doctor: 管床医生
  - virus_report: 病毒报告
  - blood_sugar: 血糖
  - blood_pressure: 血压
  - left_eye_pressure: 左眼压
  - right_eye_pressure: 右眼压
  - eye_wash_result: 冲眼结果

使用方法：
1. 备份客户的 database.db 文件
2. 将此脚本放在 backend 目录下
3. 运行: python migrate_add_fields.py
"""

import sqlite3
import os
import shutil
from datetime import datetime

def backup_database(db_path):
    """备份数据库"""
    if not os.path.exists(db_path):
        print(f"错误: 数据库文件不存在: {db_path}")
        return False
    
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✓ 数据库已备份到: {backup_path}")
        return True
    except Exception as e:
        print(f"错误: 备份失败 - {e}")
        return False

def column_exists(cursor, table_name, column_name):
    """检查列是否存在"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def add_column_if_not_exists(cursor, table_name, column_name, column_type, description=""):
    """如果列不存在则添加"""
    if column_exists(cursor, table_name, column_name):
        print(f"  - {column_name} 已存在，跳过")
        return False
    
    try:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
        print(f"  ✓ 添加字段: {column_name} ({description})")
        return True
    except Exception as e:
        print(f"  ✗ 添加字段失败 {column_name}: {e}")
        return False

def migrate_database(db_path):
    """执行数据库迁移"""
    print("\n" + "="*60)
    print("数据库迁移工具 - 添加新字段")
    print("="*60 + "\n")
    
    # 检查数据库文件
    if not os.path.exists(db_path):
        print(f"错误: 数据库文件不存在: {db_path}")
        return False
    
    # 备份数据库
    print("步骤 1: 备份数据库")
    if not backup_database(db_path):
        return False
    
    # 连接数据库
    print("\n步骤 2: 连接数据库")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("✓ 数据库连接成功")
    except Exception as e:
        print(f"错误: 数据库连接失败 - {e}")
        return False
    
    try:
        # 迁移患者表
        print("\n步骤 3: 迁移患者表(patient)")
        patient_changes = 0
        patient_changes += add_column_if_not_exists(
            cursor, "patient", "medical_card_number", "VARCHAR", "就诊卡号"
        )
        
        # 迁移预约表
        print("\n步骤 4: 迁移预约表(appointment)")
        appointment_changes = 0
        appointment_changes += add_column_if_not_exists(
            cursor, "appointment", "attending_doctor", "VARCHAR", "管床医生"
        )
        appointment_changes += add_column_if_not_exists(
            cursor, "appointment", "virus_report", "VARCHAR", "病毒报告"
        )
        appointment_changes += add_column_if_not_exists(
            cursor, "appointment", "blood_sugar", "VARCHAR", "血糖"
        )
        appointment_changes += add_column_if_not_exists(
            cursor, "appointment", "blood_pressure", "VARCHAR", "血压"
        )
        appointment_changes += add_column_if_not_exists(
            cursor, "appointment", "left_eye_pressure", "VARCHAR", "左眼压"
        )
        appointment_changes += add_column_if_not_exists(
            cursor, "appointment", "right_eye_pressure", "VARCHAR", "右眼压"
        )
        appointment_changes += add_column_if_not_exists(
            cursor, "appointment", "eye_wash_result", "VARCHAR", "冲眼结果"
        )
        
        # 提交更改
        conn.commit()
        
        # 验证迁移
        print("\n步骤 5: 验证迁移结果")
        cursor.execute("PRAGMA table_info(patient)")
        patient_columns = [row[1] for row in cursor.fetchall()]
        print(f"  患者表字段数: {len(patient_columns)}")
        
        cursor.execute("PRAGMA table_info(appointment)")
        appointment_columns = [row[1] for row in cursor.fetchall()]
        print(f"  预约表字段数: {len(appointment_columns)}")
        
        # 统计数据
        cursor.execute("SELECT COUNT(*) FROM patient")
        patient_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM appointment")
        appointment_count = cursor.fetchone()[0]
        
        print(f"\n  现有数据统计:")
        print(f"  - 患者数量: {patient_count}")
        print(f"  - 预约数量: {appointment_count}")
        
        print("\n" + "="*60)
        print("迁移完成!")
        print("="*60)
        print(f"\n总计:")
        print(f"  - 患者表新增字段: {patient_changes}")
        print(f"  - 预约表新增字段: {appointment_changes}")
        print(f"  - 现有数据完整保留")
        print(f"\n如有问题，可使用备份文件恢复")
        
        return True
        
    except Exception as e:
        print(f"\n错误: 迁移失败 - {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    
    # 数据库文件路径
    db_path = os.path.join(os.path.dirname(__file__), "database.db")
    
    print("\n警告: 此操作将修改数据库结构")
    print(f"数据库路径: {db_path}")
    
    # 检查命令行参数
    auto_confirm = "--yes" in sys.argv or "-y" in sys.argv
    
    if not auto_confirm:
        # 确认执行
        response = input("\n是否继续? (输入 yes 继续): ")
        if response.lower() != "yes":
            print("操作已取消")
            exit(0)
    else:
        print("\n自动确认模式，开始执行...")
    
    # 执行迁移
    success = migrate_database(db_path)
    
    if success:
        print("\n✓ 迁移成功! 可以启动应用程序了")
        exit(0)
    else:
        print("\n✗ 迁移失败! 请检查错误信息")
        exit(1)
