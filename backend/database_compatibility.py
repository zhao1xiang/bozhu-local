"""
数据库兼容性处理模块
确保客户数据安全的前提下解决版本兼容性问题
"""

import sqlite3
import shutil
import os
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Any

logger = logging.getLogger(__name__)

class DatabaseCompatibilityHandler:
    """数据库兼容性处理器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.backup_path = None
        self.issues_found = []
        self.fixes_applied = []
    
    def ensure_compatibility(self) -> bool:
        """确保数据库兼容性 - 主入口"""
        try:
            logger.info("🔍 开始数据库兼容性检查...")
            
            # 1. 创建安全备份
            if not self.create_safety_backup():
                logger.error("❌ 无法创建备份，停止检查")
                return False
            
            # 2. 检查兼容性问题
            issues = self.detect_compatibility_issues()
            
            if not issues:
                logger.info("✅ 数据库兼容性良好，无需修复")
                return True
            
            # 3. 应用安全修复
            logger.info(f"🔧 发现 {len(issues)} 个兼容性问题，开始修复...")
            success = self.apply_safe_fixes(issues)
            
            if success:
                logger.info("✅ 数据库兼容性修复完成")
                self.verify_data_integrity()
                return True
            else:
                logger.error("❌ 修复失败，恢复备份...")
                self.restore_backup()
                return False
                
        except Exception as e:
            logger.error(f"❌ 兼容性检查失败: {e}")
            if self.backup_path:
                self.restore_backup()
            return False
    
    def create_safety_backup(self) -> bool:
        """创建安全备份"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.backup_path = f"{self.db_path}.backup_{timestamp}"
            shutil.copy2(self.db_path, self.backup_path)
            logger.info(f"✅ 数据库已备份: {self.backup_path}")
            return True
        except Exception as e:
            logger.error(f"❌ 备份失败: {e}")
            return False
    
    def detect_compatibility_issues(self) -> List[Dict]:
        """检测兼容性问题"""
        issues = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查视力字段类型
            vision_issues = self.check_vision_field_types(cursor)
            if vision_issues:
                issues.append({
                    'type': 'vision_field_types',
                    'description': '视力字段类型需要标准化',
                    'fields': vision_issues,
                    'severity': 'medium'
                })
            
            # 检查缺失字段
            missing_fields = self.check_missing_fields(cursor)
            if missing_fields:
                issues.append({
                    'type': 'missing_fields',
                    'description': '缺少必需字段',
                    'fields': missing_fields,
                    'severity': 'low'
                })
            
            # 检查数据完整性
            integrity_issues = self.check_data_integrity(cursor)
            if integrity_issues:
                issues.append({
                    'type': 'data_integrity',
                    'description': '数据完整性问题',
                    'issues': integrity_issues,
                    'severity': 'high'
                })
            
            conn.close()
            
        except Exception as e:
            logger.error(f"检测兼容性问题时出错: {e}")
            
        return issues
    
    def check_vision_field_types(self, cursor) -> List[str]:
        """检查视力字段类型"""
        try:
            cursor.execute("PRAGMA table_info(patient)")
            columns = cursor.fetchall()
            
            vision_fields = ['left_vision', 'right_vision', 'left_vision_corrected', 'right_vision_corrected']
            problematic_fields = []
            
            for col in columns:
                col_name, col_type = col[1], col[2]
                if col_name in vision_fields and col_type == 'REAL':
                    problematic_fields.append(col_name)
            
            # 检查appointment表的视力字段
            cursor.execute("PRAGMA table_info(appointment)")
            appt_columns = cursor.fetchall()
            
            appt_vision_fields = ['pre_op_vision_left', 'pre_op_vision_right']
            for col in appt_columns:
                col_name, col_type = col[1], col[2]
                if col_name in appt_vision_fields and col_type == 'FLOAT':
                    problematic_fields.append(f"appointment.{col_name}")
            
            return problematic_fields
            
        except Exception as e:
            logger.error(f"检查视力字段类型失败: {e}")
            return []
    
    def check_missing_fields(self, cursor) -> List[Tuple]:
        """检查缺失字段"""
        try:
            # 获取当前表结构
            cursor.execute("PRAGMA table_info(patient)")
            existing_columns = [col[1] for col in cursor.fetchall()]
            
            cursor.execute("PRAGMA table_info(appointment)")
            existing_appt_columns = [col[1] for col in cursor.fetchall()]
            
            # 定义必需字段
            required_fields = {
                'patient': [
                    ('medical_card_number', 'TEXT', ''),
                    ('remarks', 'TEXT', ''),
                    ('is_deleted', 'INTEGER', '0'),
                    ('diagnosis_other', 'TEXT', ''),
                    ('drug_type_other', 'TEXT', ''),
                    ('left_vision_corrected', 'TEXT', ''),
                    ('right_vision_corrected', 'TEXT', ''),
                ],
                'appointment': [
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
                    ('treatment_phase', 'TEXT', ''),
                ]
            }
            
            missing = []
            
            # 检查患者表
            for field_name, field_type, default in required_fields['patient']:
                if field_name not in existing_columns:
                    missing.append(('patient', field_name, field_type, default))
            
            # 检查预约表
            for field_name, field_type, default in required_fields['appointment']:
                if field_name not in existing_appt_columns:
                    missing.append(('appointment', field_name, field_type, default))
            
            return missing
            
        except Exception as e:
            logger.error(f"检查缺失字段失败: {e}")
            return []
    
    def check_data_integrity(self, cursor) -> List[str]:
        """检查数据完整性"""
        issues = []
        
        try:
            # 检查患者表
            cursor.execute("SELECT COUNT(*) FROM patient WHERE name IS NULL OR name = ''")
            if cursor.fetchone()[0] > 0:
                issues.append("患者表中存在空姓名记录")
            
            # 检查预约表
            cursor.execute("SELECT COUNT(*) FROM appointment WHERE patient_id IS NULL OR patient_id = ''")
            if cursor.fetchone()[0] > 0:
                issues.append("预约表中存在空患者ID记录")
            
        except Exception as e:
            logger.error(f"检查数据完整性失败: {e}")
            
        return issues
    
    def apply_safe_fixes(self, issues: List[Dict]) -> bool:
        """应用安全修复"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for issue in issues:
                if issue['type'] == 'missing_fields':
                    self.fix_missing_fields(cursor, issue['fields'])
                elif issue['type'] == 'vision_field_types':
                    self.fix_vision_field_types_safe(cursor, issue['fields'])
                    # 对于appointment表的FLOAT字段，需要重建表结构
                    self.fix_appointment_vision_fields(cursor, issue['fields'])
                elif issue['type'] == 'data_integrity':
                    self.fix_data_integrity_issues(cursor, issue['issues'])
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"应用修复失败: {e}")
            try:
                conn.rollback()
                conn.close()
            except:
                pass
            return False
    
    def fix_missing_fields(self, cursor, missing_fields: List[Tuple]):
        """修复缺失字段"""
        for table, field_name, field_type, default in missing_fields:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {field_name} {field_type} DEFAULT '{default}'")
                logger.info(f"  ✅ 添加字段: {table}.{field_name}")
                self.fixes_applied.append(f"添加字段 {table}.{field_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    logger.info(f"  ℹ️  字段已存在: {table}.{field_name}")
                else:
                    raise
    
    def fix_vision_field_types_safe(self, cursor, problematic_fields: List[str]):
        """安全修复视力字段类型 - 不重建表，只标准化数据"""
        for field in problematic_fields:
            try:
                if field.startswith("appointment."):
                    # 处理appointment表的字段
                    field_name = field.replace("appointment.", "")
                    table_name = "appointment"
                else:
                    # 处理patient表的字段
                    field_name = field
                    table_name = "patient"
                
                # 标准化数据：NULL -> '', 0 -> '', 其他数字 -> 字符串
                cursor.execute(f"""
                    UPDATE {table_name} 
                    SET {field_name} = CASE 
                        WHEN {field_name} IS NULL THEN ''
                        WHEN {field_name} = 0 THEN ''
                        WHEN {field_name} = 0.0 THEN ''
                        ELSE CAST({field_name} AS TEXT)
                    END
                """)
                
                affected_rows = cursor.rowcount
                logger.info(f"  ✅ 标准化字段 {table_name}.{field_name}: {affected_rows} 条记录")
                self.fixes_applied.append(f"标准化视力字段 {table_name}.{field_name}")
                
            except Exception as e:
                logger.error(f"  ❌ 修复字段 {field} 失败: {e}")
                raise
    
    def fix_data_integrity_issues(self, cursor, issues: List[str]):
        """修复数据完整性问题"""
        for issue in issues:
            logger.warning(f"  ⚠️  数据完整性问题: {issue}")
            # 这里可以添加具体的修复逻辑
            # 但要非常小心，避免数据丢失
    
    def fix_appointment_vision_fields(self, cursor, problematic_fields: List[str]):
        """修复appointment表的视力字段类型（FLOAT -> TEXT）"""
        appointment_vision_fields = []
        for field in problematic_fields:
            if field.startswith("appointment."):
                appointment_vision_fields.append(field.replace("appointment.", ""))
        
        if not appointment_vision_fields:
            return
        
        try:
            logger.info(f"  🔧 修复appointment表视力字段类型: {appointment_vision_fields}")
            
            # 1. 获取原表的所有字段信息
            cursor.execute("PRAGMA table_info(appointment)")
            original_columns = cursor.fetchall()
            
            # 2. 创建临时表
            cursor.execute("""
                CREATE TABLE appointment_temp AS 
                SELECT * FROM appointment
            """)
            
            # 3. 删除原表
            cursor.execute("DROP TABLE appointment")
            
            # 4. 重新创建表，保持原有字段顺序，只修改视力字段类型
            create_fields = []
            for col in original_columns:
                col_name = col[1]
                col_type = col[2]
                not_null = col[3]
                default_val = col[4]
                is_pk = col[5]
                
                # 如果是需要修改的视力字段，改为TEXT类型
                if col_name in appointment_vision_fields:
                    col_type = 'TEXT'
                    default_val = "''"
                
                # 构建字段定义
                field_def = f"{col_name} {col_type}"
                
                if is_pk:
                    field_def += " PRIMARY KEY"
                elif not_null:
                    field_def += " NOT NULL"
                
                if default_val is not None and not is_pk:
                    if col_type in ['TEXT', 'VARCHAR']:
                        field_def += f" DEFAULT {default_val}" if default_val.startswith("'") else f" DEFAULT '{default_val}'"
                    else:
                        field_def += f" DEFAULT {default_val}"
                
                create_fields.append(field_def)
            
            # 添加外键约束
            create_fields.append("FOREIGN KEY (patient_id) REFERENCES patient (id)")
            
            create_sql = f"CREATE TABLE appointment ({', '.join(create_fields)})"
            cursor.execute(create_sql)
            
            # 5. 复制数据，转换视力字段
            # 获取所有字段名
            column_names = [col[1] for col in original_columns]
            
            # 构建SELECT语句，对视力字段进行类型转换
            select_parts = []
            for col_name in column_names:
                if col_name in appointment_vision_fields:
                    # 转换FLOAT到TEXT
                    select_parts.append(f"""
                        CASE 
                            WHEN {col_name} IS NULL THEN ''
                            WHEN {col_name} = 0 THEN ''
                            WHEN {col_name} = 0.0 THEN ''
                            ELSE CAST({col_name} AS TEXT)
                        END AS {col_name}
                    """.strip())
                else:
                    select_parts.append(col_name)
            
            # 构建INSERT语句
            insert_sql = f"""
                INSERT INTO appointment ({', '.join(column_names)})
                SELECT {', '.join(select_parts)}
                FROM appointment_temp
            """
            
            cursor.execute(insert_sql)
            
            # 6. 删除临时表
            cursor.execute("DROP TABLE appointment_temp")
            
            # 7. 重建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_appointment_patient_id ON appointment (patient_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_appointment_appointment_date ON appointment (appointment_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_appointment_status ON appointment (status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_appointment_is_deleted ON appointment (is_deleted)")
            
            affected_rows = cursor.rowcount
            logger.info(f"  ✅ appointment表视力字段类型修复完成: {affected_rows} 条记录")
            self.fixes_applied.append("修复appointment表视力字段类型 FLOAT->TEXT")
            
        except Exception as e:
            logger.error(f"  ❌ 修复appointment表视力字段失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # 尝试恢复
            try:
                cursor.execute("DROP TABLE IF EXISTS appointment")
                cursor.execute("ALTER TABLE appointment_temp RENAME TO appointment")
                logger.info("  🔄 已恢复原表结构")
            except:
                pass
            raise
    
    def verify_data_integrity(self):
        """验证数据完整性"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 统计记录数
            cursor.execute("SELECT COUNT(*) FROM patient WHERE is_deleted = 0")
            patient_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM appointment WHERE is_deleted = 0")
            appointment_count = cursor.fetchone()[0]
            
            logger.info(f"📊 数据验证: 患者 {patient_count} 人, 预约 {appointment_count} 条")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"数据完整性验证失败: {e}")
    
    def restore_backup(self):
        """恢复备份"""
        if self.backup_path and os.path.exists(self.backup_path):
            try:
                shutil.copy2(self.backup_path, self.db_path)
                logger.info(f"✅ 已恢复备份: {self.backup_path}")
            except Exception as e:
                logger.error(f"❌ 恢复备份失败: {e}")

def ensure_database_compatibility(db_path: str) -> bool:
    """确保数据库兼容性 - 外部接口"""
    handler = DatabaseCompatibilityHandler(db_path)
    return handler.ensure_compatibility()

if __name__ == "__main__":
    # 独立运行的兼容性检查工具
    import sys
    
    db_path = sys.argv[1] if len(sys.argv) > 1 else "database.db"
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        sys.exit(1)
    
    print(f"🔍 检查数据库兼容性: {db_path}")
    success = ensure_database_compatibility(db_path)
    
    if success:
        print("✅ 数据库兼容性检查完成")
        sys.exit(0)
    else:
        print("❌ 数据库兼容性检查失败")
        sys.exit(1)