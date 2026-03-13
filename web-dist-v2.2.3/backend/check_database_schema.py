"""
数据库结构检查工具
用于验证数据库是否包含所有必需的字段
"""

import sqlite3
import os

def check_database_schema(db_path):
    """检查数据库结构"""
    print("\n" + "="*60)
    print("数据库结构检查工具")
    print("="*60 + "\n")
    
    if not os.path.exists(db_path):
        print(f"错误: 数据库文件不存在: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查患者表
        print("检查患者表(patient):")
        cursor.execute("PRAGMA table_info(patient)")
        patient_columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        required_patient_fields = {
            'medical_card_number': 'VARCHAR'
        }
        
        patient_ok = True
        for field, field_type in required_patient_fields.items():
            if field in patient_columns:
                print(f"  ✓ {field}")
            else:
                print(f"  ✗ {field} - 缺失")
                patient_ok = False
        
        # 检查预约表
        print("\n检查预约表(appointment):")
        cursor.execute("PRAGMA table_info(appointment)")
        appointment_columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        required_appointment_fields = {
            'attending_doctor': 'VARCHAR',
            'virus_report': 'VARCHAR',
            'blood_sugar': 'VARCHAR',
            'blood_pressure': 'VARCHAR',
            'left_eye_pressure': 'VARCHAR',
            'right_eye_pressure': 'VARCHAR',
            'eye_wash_result': 'VARCHAR'
        }
        
        appointment_ok = True
        for field, field_type in required_appointment_fields.items():
            if field in appointment_columns:
                print(f"  ✓ {field}")
            else:
                print(f"  ✗ {field} - 缺失")
                appointment_ok = False
        
        # 统计数据
        cursor.execute("SELECT COUNT(*) FROM patient")
        patient_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM appointment")
        appointment_count = cursor.fetchone()[0]
        
        print(f"\n数据统计:")
        print(f"  - 患者数量: {patient_count}")
        print(f"  - 预约数量: {appointment_count}")
        
        print("\n" + "="*60)
        if patient_ok and appointment_ok:
            print("✓ 数据库结构检查通过")
            print("="*60)
            return True
        else:
            print("✗ 数据库结构检查失败 - 缺少必需字段")
            print("="*60)
            print("\n建议: 运行 升级数据库.bat 进行升级")
            return False
        
    except Exception as e:
        print(f"\n错误: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    db_path = os.path.join(os.path.dirname(__file__), "database.db")
    success = check_database_schema(db_path)
    exit(0 if success else 1)
