#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""完整的数据库迁移脚本 - 添加所有缺失的列"""

import sqlite3

def migrate():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    print("=" * 60)
    print("开始数据库迁移")
    print("=" * 60)
    
    # 检查并迁移 patient 表
    print("\n检查 patient 表...")
    cursor.execute("PRAGMA table_info(patient)")
    patient_cols = [col[1] for col in cursor.fetchall()]
    print(f"现有列: {', '.join(patient_cols)}")
    
    patient_new_cols = {
        'medical_card_number': 'TEXT',
        'patient_type': 'TEXT',
        'injection_count': 'INTEGER'
    }
    
    for col_name, col_type in patient_new_cols.items():
        if col_name not in patient_cols:
            print(f"  添加列: {col_name} ({col_type})")
            cursor.execute(f"ALTER TABLE patient ADD COLUMN {col_name} {col_type}")
        else:
            print(f"  ✓ 列已存在: {col_name}")
    
    # 检查并迁移 appointment 表
    print("\n检查 appointment 表...")
    cursor.execute("PRAGMA table_info(appointment)")
    appointment_cols = [col[1] for col in cursor.fetchall()]
    print(f"现有列: {', '.join(appointment_cols)}")
    
    appointment_new_cols = {
        'attending_doctor': 'TEXT',
        'virus_report': 'TEXT',
        'blood_sugar': 'TEXT',
        'blood_pressure': 'TEXT',
        'left_eye_pressure': 'TEXT',
        'right_eye_pressure': 'TEXT',
        'eye_wash_result': 'TEXT',
        'treatment_phase': 'TEXT',
        'pre_op_vision_left': 'REAL',
        'pre_op_vision_right': 'REAL'
    }
    
    for col_name, col_type in appointment_new_cols.items():
        if col_name not in appointment_cols:
            print(f"  添加列: {col_name} ({col_type})")
            cursor.execute(f"ALTER TABLE appointment ADD COLUMN {col_name} {col_type}")
        else:
            print(f"  ✓ 列已存在: {col_name}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ 数据库迁移完成！")
    print("=" * 60)

if __name__ == "__main__":
    migrate()
