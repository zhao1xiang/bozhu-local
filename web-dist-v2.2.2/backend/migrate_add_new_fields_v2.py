"""
数据库迁移脚本 - 添加新字段 v2
1. 患者表：diagnosis_other, drug_type_other, left_vision_corrected, right_vision_corrected
2. 预约表：drug_name_other
3. 系统配置：初始化注射周期和打印电话
"""
import sqlite3
import os
from datetime import datetime

def migrate_database():
    db_path = "database.db"
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    # 备份数据库
    backup_path = f"database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    import shutil
    shutil.copy2(db_path, backup_path)
    print(f"✓ 数据库已备份到: {backup_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 获取患者表的列
        cursor.execute("PRAGMA table_info(patient)")
        patient_columns = [row[1] for row in cursor.fetchall()]
        
        # 添加患者表新字段
        new_patient_fields = [
            ("diagnosis_other", "TEXT"),
            ("drug_type_other", "TEXT"),
            ("left_vision_corrected", "REAL"),
            ("right_vision_corrected", "REAL"),
        ]
        
        for field_name, field_type in new_patient_fields:
            if field_name not in patient_columns:
                cursor.execute(f"ALTER TABLE patient ADD COLUMN {field_name} {field_type}")
                print(f"✓ 患者表添加字段: {field_name}")
            else:
                print(f"- 患者表字段已存在: {field_name}")
        
        # 获取预约表的列
        cursor.execute("PRAGMA table_info(appointment)")
        appointment_columns = [row[1] for row in cursor.fetchall()]
        
        # 添加预约表新字段
        if "drug_name_other" not in appointment_columns:
            cursor.execute("ALTER TABLE appointment ADD COLUMN drug_name_other TEXT")
            print(f"✓ 预约表添加字段: drug_name_other")
        else:
            print(f"- 预约表字段已存在: drug_name_other")
        
        # 初始化系统配置
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='systemsetting'")
        if cursor.fetchone():
            # 检查并添加注射周期配置
            cursor.execute("SELECT * FROM systemsetting WHERE key='injection_interval_first_4'")
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO systemsetting (key, value, description, updated_at)
                    VALUES ('injection_interval_first_4', '30', '前4针注射间隔（天）', datetime('now'))
                """)
                print("✓ 添加系统配置: injection_interval_first_4 = 30")
            else:
                print("- 系统配置已存在: injection_interval_first_4")
            
            # 检查并添加打印电话配置
            cursor.execute("SELECT * FROM systemsetting WHERE key='print_phone_number'")
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO systemsetting (key, value, description, updated_at)
                    VALUES ('print_phone_number', '13608685716', '打印页面显示的联系电话', datetime('now'))
                """)
                print("✓ 添加系统配置: print_phone_number = 13608685716")
            else:
                print("- 系统配置已存在: print_phone_number")
        else:
            print("⚠ systemsetting 表不存在，跳过系统配置初始化")
        
        conn.commit()
        print("\n✓ 数据库迁移完成！")
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
