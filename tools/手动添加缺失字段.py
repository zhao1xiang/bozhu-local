"""
手动添加缺失字段工具
用于手动为客户数据库添加缺失的字段
"""

import sqlite3
import shutil
from datetime import datetime

def add_missing_fields(db_path="database.db"):
    """手动添加缺失字段"""
    
    # 创建备份
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✅ 数据库已备份: {backup_path}")
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("手动添加缺失字段工具 - v2.2.3")
        print("=" * 60)
        print()
        
        # 患者表需要添加的字段
        patient_fields = [
            ('medical_card_number', 'TEXT', ''),
            ('remarks', 'TEXT', ''),
            ('is_deleted', 'INTEGER', '0'),
            ('diagnosis_other', 'TEXT', ''),
            ('drug_type_other', 'TEXT', ''),
            ('left_vision_corrected', 'TEXT', ''),
            ('right_vision_corrected', 'TEXT', ''),
        ]
        
        # 预约表需要添加的字段
        appointment_fields = [
            ('attending_doctor', 'TEXT', ''),
            ('virus_report', 'TEXT', ''),
            ('blood_sugar', 'TEXT', ''),
            ('blood_pressure', 'TEXT', ''),
            ('left_eye_pressure', 'TEXT', ''),
            ('right_eye_pressure', 'TEXT', ''),
            ('eye_wash_result', 'TEXT', ''),
            ('is_deleted', 'INTEGER', '0'),
            ('drug_name_other', 'TEXT', ''),
            ('pre_op_vision_left', 'TEXT', ''),
            ('pre_op_vision_right', 'TEXT', ''),
            ('pre_op_vision_left_corrected', 'TEXT', ''),
            ('pre_op_vision_right_corrected', 'TEXT', ''),
            ('treatment_phase', 'TEXT', ''),
        ]
        
        print("【处理患者表 (patient)】")
        for field_name, field_type, default in patient_fields:
            try:
                if field_type == 'INTEGER':
                    cursor.execute(f"ALTER TABLE patient ADD COLUMN {field_name} {field_type} DEFAULT {default}")
                else:
                    cursor.execute(f"ALTER TABLE patient ADD COLUMN {field_name} {field_type} DEFAULT '{default}'")
                print(f"  ✅ 添加字段: {field_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"  ℹ️  字段已存在: {field_name}")
                else:
                    print(f"  ❌ 添加失败: {field_name} - {e}")
        
        print()
        print("【处理预约表 (appointment)】")
        for field_name, field_type, default in appointment_fields:
            try:
                if field_type == 'INTEGER':
                    cursor.execute(f"ALTER TABLE appointment ADD COLUMN {field_name} {field_type} DEFAULT {default}")
                else:
                    cursor.execute(f"ALTER TABLE appointment ADD COLUMN {field_name} {field_type} DEFAULT '{default}'")
                print(f"  ✅ 添加字段: {field_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"  ℹ️  字段已存在: {field_name}")
                else:
                    print(f"  ❌ 添加失败: {field_name} - {e}")
        
        conn.commit()
        conn.close()
        
        print()
        print("=" * 60)
        print("✅ 字段添加完成！")
        print("=" * 60)
        print()
        print("请重启系统以使更改生效。")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        print(f"正在恢复备份...")
        try:
            shutil.copy2(backup_path, db_path)
            print(f"✅ 已恢复备份")
        except:
            print(f"❌ 恢复失败，请手动从 {backup_path} 恢复")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = "database.db"
    
    print()
    print("⚠️  警告：此工具将修改数据库结构")
    print("请确保已关闭系统，并且已备份数据库文件")
    print()
    
    response = input("是否继续？(y/n): ")
    if response.lower() == 'y':
        add_missing_fields(db_path)
    else:
        print("已取消操作")
