"""
测试数据库迁移功能
"""
import sqlite3
import os
import shutil

# 备份当前数据库
if os.path.exists("database.db"):
    shutil.copy2("database.db", "database.db.test_backup")
    print("✓ 已备份当前数据库")

# 删除新字段，模拟旧数据库
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

print("\n删除新字段，模拟旧数据库...")

# 患者表 - 删除 medical_card_number
try:
    # SQLite 不支持直接删除列，需要重建表
    cursor.execute("PRAGMA table_info(patient)")
    columns = cursor.fetchall()
    
    # 过滤掉 medical_card_number
    old_columns = [col[1] for col in columns if col[1] != 'medical_card_number']
    
    # 创建临时表
    cursor.execute(f"""
        CREATE TABLE patient_temp AS 
        SELECT {', '.join(old_columns)} FROM patient
    """)
    
    # 删除旧表
    cursor.execute("DROP TABLE patient")
    
    # 重命名临时表
    cursor.execute("ALTER TABLE patient_temp RENAME TO patient")
    
    # 重建索引
    cursor.execute("CREATE INDEX ix_patient_name ON patient (name)")
    cursor.execute("CREATE INDEX ix_patient_status ON patient (status)")
    cursor.execute("CREATE UNIQUE INDEX ix_patient_phone ON patient (phone)")
    cursor.execute("CREATE UNIQUE INDEX ix_patient_outpatient_number ON patient (outpatient_number)")
    
    print("✓ 患者表：已删除 medical_card_number")
except Exception as e:
    print(f"✗ 患者表处理失败: {e}")

# 预约表 - 删除新字段
try:
    cursor.execute("PRAGMA table_info(appointment)")
    columns = cursor.fetchall()
    
    # 过滤掉新字段
    exclude_fields = ['attending_doctor', 'virus_report', 'blood_sugar', 'blood_pressure', 
                     'left_eye_pressure', 'right_eye_pressure', 'eye_wash_result']
    old_columns = [col[1] for col in columns if col[1] not in exclude_fields]
    
    # 创建临时表
    cursor.execute(f"""
        CREATE TABLE appointment_temp AS 
        SELECT {', '.join(old_columns)} FROM appointment
    """)
    
    # 删除旧表
    cursor.execute("DROP TABLE appointment")
    
    # 重命名临时表
    cursor.execute("ALTER TABLE appointment_temp RENAME TO appointment")
    
    # 重建索引
    cursor.execute("CREATE INDEX ix_appointment_status ON appointment (status)")
    cursor.execute("CREATE INDEX ix_appointment_appointment_date ON appointment (appointment_date)")
    cursor.execute("CREATE INDEX ix_appointment_patient_id ON appointment (patient_id)")
    
    print("✓ 预约表：已删除 7 个新字段")
except Exception as e:
    print(f"✗ 预约表处理失败: {e}")

conn.commit()
conn.close()

print("\n✓ 旧数据库模拟完成")
print("现在可以测试自动迁移功能了")
print("\n恢复数据库：")
print("  copy database.db.test_backup database.db")
