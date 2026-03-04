"""
自动数据库迁移模块
在应用启动时自动检测并升级数据库结构
完全静默，不需要用户操作
"""

import sqlite3
import os
import shutil
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def backup_database(db_path):
    """备份数据库（静默）"""
    if not os.path.exists(db_path):
        return False
    
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        shutil.copy2(db_path, backup_path)
        logger.info(f"数据库已备份: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"数据库备份失败: {e}")
        return False

def column_exists(cursor, table_name, column_name):
    """检查列是否存在"""
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        return column_name in columns
    except Exception as e:
        logger.error(f"检查列失败 {table_name}.{column_name}: {e}")
        return False

def add_column_safe(cursor, table_name, column_name, column_type, description=""):
    """安全地添加列（如果不存在）"""
    if column_exists(cursor, table_name, column_name):
        logger.debug(f"字段已存在，跳过: {table_name}.{column_name}")
        return False
    
    try:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
        logger.info(f"✓ 添加字段: {table_name}.{column_name} ({description})")
        return True
    except Exception as e:
        logger.error(f"✗ 添加字段失败 {table_name}.{column_name}: {e}")
        return False

def auto_migrate_database(db_path=None):
    """
    自动迁移数据库
    返回: (success: bool, changes_made: int, message: str)
    """
    if db_path is None:
        db_path = os.path.join(os.path.dirname(__file__), "database.db")
    
    # 检查数据库文件
    if not os.path.exists(db_path):
        logger.warning(f"数据库文件不存在: {db_path}")
        return False, 0, "数据库文件不存在"
    
    logger.info("=" * 60)
    logger.info("开始自动数据库迁移检查...")
    logger.info("=" * 60)
    
    changes_made = 0
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 定义需要的字段
        migrations = {
            'patient': [
                ('medical_card_number', 'VARCHAR', '就诊卡号'),
            ],
            'appointment': [
                ('attending_doctor', 'VARCHAR', '管床医生'),
                ('virus_report', 'VARCHAR', '病毒报告'),
                ('blood_sugar', 'VARCHAR', '血糖'),
                ('blood_pressure', 'VARCHAR', '血压'),
                ('left_eye_pressure', 'VARCHAR', '左眼压'),
                ('right_eye_pressure', 'VARCHAR', '右眼压'),
                ('eye_wash_result', 'VARCHAR', '冲眼结果'),
            ]
        }
        
        # 检查是否需要迁移
        needs_migration = False
        for table_name, fields in migrations.items():
            for field_name, field_type, description in fields:
                if not column_exists(cursor, table_name, field_name):
                    needs_migration = True
                    break
            if needs_migration:
                break
        
        # 如果需要迁移，先备份
        if needs_migration:
            logger.info("检测到需要升级数据库结构")
            if backup_database(db_path):
                logger.info("数据库备份成功，开始升级...")
            else:
                logger.warning("数据库备份失败，但继续升级...")
        else:
            logger.info("数据库结构已是最新，无需升级")
            conn.close()
            return True, 0, "数据库已是最新"
        
        # 执行迁移
        for table_name, fields in migrations.items():
            logger.info(f"检查表: {table_name}")
            for field_name, field_type, description in fields:
                if add_column_safe(cursor, table_name, field_name, field_type, description):
                    changes_made += 1
        
        # 提交更改
        conn.commit()
        
        # 验证迁移
        logger.info("验证迁移结果...")
        all_ok = True
        for table_name, fields in migrations.items():
            for field_name, field_type, description in fields:
                if not column_exists(cursor, table_name, field_name):
                    logger.error(f"验证失败: {table_name}.{field_name} 不存在")
                    all_ok = False
        
        if all_ok:
            logger.info("=" * 60)
            logger.info(f"✓ 数据库迁移成功! 新增 {changes_made} 个字段")
            logger.info("=" * 60)
            conn.close()
            return True, changes_made, f"成功添加 {changes_made} 个字段"
        else:
            logger.error("=" * 60)
            logger.error("✗ 数据库迁移验证失败")
            logger.error("=" * 60)
            conn.close()
            return False, changes_made, "迁移验证失败"
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"数据库迁移失败: {e}")
        logger.error("=" * 60)
        import traceback
        logger.error(traceback.format_exc())
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        return False, 0, f"迁移失败: {str(e)}"

def check_and_migrate():
    """
    检查并执行数据库迁移（供启动脚本调用）
    返回: bool - 是否成功
    """
    try:
        success, changes, message = auto_migrate_database()
        if success:
            if changes > 0:
                logger.info(f"数据库已自动升级: {message}")
            return True
        else:
            logger.error(f"数据库迁移失败: {message}")
            return False
    except Exception as e:
        logger.error(f"数据库迁移异常: {e}")
        return False

if __name__ == "__main__":
    # 测试用
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    success, changes, message = auto_migrate_database()
    print(f"\n结果: {'成功' if success else '失败'}")
    print(f"变更: {changes} 个字段")
    print(f"消息: {message}")
