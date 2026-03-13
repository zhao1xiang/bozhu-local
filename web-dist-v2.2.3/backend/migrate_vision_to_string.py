"""
数据库迁移脚本：将视力字段从数字类型改为字符串类型
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

def migrate():
    """执行迁移"""
    db_path = "database.db"
    
    print("=" * 60)
    print("数据库迁移：视力字段类型转换（数字→字符串）")
    print("=" * 60)
    print()
    
    # 检查数据库文件
    if not os.path.exists(db_path):
        print(f"✗ 数据库文件不存在: {db_path}")
        return False
    
    # 备份数据库
    print("[1/4] 备份数据库...")
    if not backup_database(db_path):
        print("⚠ 备份失败，但继续执行迁移...")
    print()
    
    # 连接数据库
    print("[2/4] 连接数据库...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("✓ 数据库连接成功")
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return False
    print()
    
    try:
        # 执行迁移
        print("[3/4] 执行迁移...")
        print("  注意：SQLite不支持直接修改列类型")
        print("  将创建新表，复制数据，然后替换旧表")
        print()
        
        # 1. 创建新表
        print("  [1/5] 创建新表 patient_new...")
        cursor.execute("""
            CREATE TABLE patient_new (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                outpatient_number TEXT,
                medical_card_number TEXT,
                phone TEXT NOT NULL UNIQUE,
                diagnosis TEXT,
                diagnosis_other TEXT,
                drug_type TEXT,
                drug_type_other TEXT,
                left_vision TEXT,
                right_vision TEXT,
                left_vision_corrected TEXT,
                right_vision_corrected TEXT,
                left_eye INTEGER NOT NULL DEFAULT 0,
                right_eye INTEGER NOT NULL DEFAULT 0,
                patient_type TEXT,
                injection_count INTEGER,
                remarks TEXT,
                status TEXT NOT NULL DEFAULT 'active',
                is_deleted INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        print("  ✓ 新表创建成功")
        
        # 2. 复制数据（将数字转为字符串）
        print("  [2/5] 复制数据到新表...")
        cursor.execute("""
            INSERT INTO patient_new (
                id, name, outpatient_number, medical_card_number, phone,
                diagnosis, drug_type,
                left_vision, right_vision,
                left_eye, right_eye, patient_type, injection_count,
                status, created_at, updated_at, remarks
            )
            SELECT 
                id, name, outpatient_number, medical_card_number, phone,
                diagnosis, drug_type,
                CAST(left_vision AS TEXT),
                CAST(right_vision AS TEXT),
                left_eye, right_eye, patient_type, injection_count,
                status, created_at, updated_at, remarks
            FROM patient
        """)
        rows_copied = cursor.rowcount
        print(f"  ✓ 已复制 {rows_copied} 条记录")
        
        # 3. 删除旧表
        print("  [3/5] 删除旧表...")
        cursor.execute("DROP TABLE patient")
        print("  ✓ 旧表已删除")
        
        # 4. 重命名新表
        print("  [4/5] 重命名新表...")
        cursor.execute("ALTER TABLE patient_new RENAME TO patient")
        print("  ✓ 新表已重命名为 patient")
        
        # 5. 重建索引
        print("  [5/5] 重建索引...")
        cursor.execute("CREATE INDEX idx_patient_name ON patient(name)")
        cursor.execute("CREATE INDEX idx_patient_outpatient_number ON patient(outpatient_number)")
        cursor.execute("CREATE INDEX idx_patient_phone ON patient(phone)")
        cursor.execute("CREATE INDEX idx_patient_status ON patient(status)")
        cursor.execute("CREATE INDEX idx_patient_is_deleted ON patient(is_deleted)")
        print("  ✓ 索引已重建")
        
        # 提交更改
        conn.commit()
        print()
        
        # 验证迁移
        print("[4/4] 验证迁移结果...")
        cursor.execute("PRAGMA table_info(patient)")
        columns = cursor.fetchall()
        
        vision_fields = ['left_vision', 'right_vision', 'left_vision_corrected', 'right_vision_corrected']
        all_ok = True
        
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            if col_name in vision_fields:
                if col_type == 'TEXT':
                    print(f"  ✓ {col_name}: {col_type}")
                else:
                    print(f"  ✗ {col_name}: {col_type} (应该是 TEXT)")
                    all_ok = False
        
        if all_ok:
            print()
            print("=" * 60)
            print(f"✓ 迁移完成! 已将 {rows_copied} 条记录的视力字段转换为字符串类型")
            print("=" * 60)
            conn.close()
            return True
        else:
            print()
            print("=" * 60)
            print("✗ 迁移验证失败")
            print("=" * 60)
            conn.close()
            return False
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ 迁移失败: {e}")
        print("=" * 60)
        import traceback
        print(traceback.format_exc())
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        return False

if __name__ == "__main__":
    success = migrate()
    if success:
        print("\n迁移成功！视力字段现在支持输入中文了。")
    else:
        print("\n迁移失败！请检查错误信息。")
    
    input("\n按回车键退出...")
