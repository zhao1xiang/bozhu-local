"""
数据库字段检查诊断工具
用于检查客户数据库是否缺少必需字段
"""

import sqlite3
import sys

def check_database_fields(db_path="database.db"):
    """检查数据库字段"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("数据库字段检查诊断工具 - v2.2.3")
        print("=" * 60)
        print()
        
        # 检查患者表
        print("【患者表 (patient) 字段检查】")
        cursor.execute("PRAGMA table_info(patient)")
        patient_columns = [col[1] for col in cursor.fetchall()]
        
        required_patient_fields = [
            'medical_card_number',
            'remarks',
            'is_deleted',
            'diagnosis_other',
            'drug_type_other',
            'left_vision_corrected',
            'right_vision_corrected',
        ]
        
        missing_patient = []
        for field in required_patient_fields:
            if field in patient_columns:
                print(f"  ✅ {field}")
            else:
                print(f"  ❌ {field} - 缺失")
                missing_patient.append(field)
        
        print()
        
        # 检查预约表
        print("【预约表 (appointment) 字段检查】")
        cursor.execute("PRAGMA table_info(appointment)")
        appointment_columns = [col[1] for col in cursor.fetchall()]
        
        required_appointment_fields = [
            'attending_doctor',
            'virus_report',
            'blood_sugar',
            'blood_pressure',
            'left_eye_pressure',
            'right_eye_pressure',
            'eye_wash_result',
            'is_deleted',
            'drug_name_other',
            'pre_op_vision_left',
            'pre_op_vision_right',
            'pre_op_vision_left_corrected',
            'pre_op_vision_right_corrected',
            'treatment_phase',
        ]
        
        missing_appointment = []
        for field in required_appointment_fields:
            if field in appointment_columns:
                print(f"  ✅ {field}")
            else:
                print(f"  ❌ {field} - 缺失")
                missing_appointment.append(field)
        
        print()
        print("=" * 60)
        
        if missing_patient or missing_appointment:
            print("⚠️  发现缺失字段！")
            print()
            if missing_patient:
                print(f"患者表缺失字段: {', '.join(missing_patient)}")
            if missing_appointment:
                print(f"预约表缺失字段: {', '.join(missing_appointment)}")
            print()
            print("解决方案：")
            print("1. 确认使用的是最新版本的 backend_server.exe")
            print("2. 重启系统，系统会自动添加缺失字段")
            print("3. 如果问题仍然存在，请联系技术支持")
        else:
            print("✅ 所有必需字段都存在，数据库结构正常")
        
        print("=" * 60)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = "database.db"
    
    check_database_fields(db_path)
