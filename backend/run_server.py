"""
后端服务器启动脚本
用于 PyInstaller 打包后的独立运行
包含自动数据库迁移功能
"""
import uvicorn
import sys
import os
import logging
import sqlite3
import shutil
from datetime import datetime

# 应用版本号
APP_VERSION = "2.1.2"
APP_NAME = "眼科注射预约系统后端"

# ==================== 自动数据库迁移功能 ====================

def backup_database_silent(db_path):
    """静默备份数据库"""
    if not os.path.exists(db_path):
        return False
    
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        shutil.copy2(db_path, backup_path)
        logging.info(f"数据库已备份: {backup_path}")
        return True
    except Exception as e:
        logging.error(f"数据库备份失败: {e}")
        return False

def column_exists_check(cursor, table_name, column_name):
    """检查列是否存在"""
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        return column_name in columns
    except Exception as e:
        logging.error(f"检查列失败 {table_name}.{column_name}: {e}")
        return False

def add_column_safe_exec(cursor, table_name, column_name, column_type, description=""):
    """安全地添加列（如果不存在）"""
    if column_exists_check(cursor, table_name, column_name):
        logging.debug(f"字段已存在，跳过: {table_name}.{column_name}")
        return False
    
    try:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
        logging.info(f"✓ 添加字段: {table_name}.{column_name} ({description})")
        return True
    except Exception as e:
        logging.error(f"✗ 添加字段失败 {table_name}.{column_name}: {e}")
        return False

def auto_migrate_on_startup(db_path):
    """启动时自动迁移数据库"""
    logger = logging.getLogger(__name__)
    
    if not os.path.exists(db_path):
        logger.warning(f"数据库文件不存在: {db_path}")
        return False
    
    logger.info("=" * 60)
    logger.info("开始自动数据库迁移检查...")
    logger.info("=" * 60)
    
    changes_made = 0
    
    try:
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
                if not column_exists_check(cursor, table_name, field_name):
                    needs_migration = True
                    break
            if needs_migration:
                break
        
        # 如果需要迁移，先备份
        if needs_migration:
            logger.info("检测到需要升级数据库结构")
            if backup_database_silent(db_path):
                logger.info("数据库备份成功，开始升级...")
            else:
                logger.warning("数据库备份失败，但继续升级...")
        else:
            logger.info("数据库结构已是最新，无需升级")
            conn.close()
            return True
        
        # 执行迁移
        for table_name, fields in migrations.items():
            logger.info(f"检查表: {table_name}")
            for field_name, field_type, description in fields:
                if add_column_safe_exec(cursor, table_name, field_name, field_type, description):
                    changes_made += 1
        
        # 提交更改
        conn.commit()
        
        # 验证迁移
        logger.info("验证迁移结果...")
        all_ok = True
        for table_name, fields in migrations.items():
            for field_name, field_type, description in fields:
                if not column_exists_check(cursor, table_name, field_name):
                    logger.error(f"验证失败: {table_name}.{field_name} 不存在")
                    all_ok = False
        
        if all_ok:
            logger.info("=" * 60)
            logger.info(f"✓ 数据库迁移成功! 新增 {changes_made} 个字段")
            logger.info("=" * 60)
            conn.close()
            return True
        else:
            logger.error("=" * 60)
            logger.error("✗ 数据库迁移验证失败")
            logger.error("=" * 60)
            conn.close()
            return False
        
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
        return False

# ==================== 日志配置 ====================
def setup_logging():
    # 获取当前工作目录
    current_dir = os.getcwd()
    
    # 日志文件在 logs 文件夹（同级目录）
    logs_dir = os.path.join(current_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    log_file = os.path.join(logs_dir, "backend.log")
    
    # 创建日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)
    
    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 清除已有的处理器（避免重复）
    root_logger.handlers.clear()
    
    # 创建文件处理器（UTF-8 编码）
    file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='a')
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # 创建控制台处理器（UTF-8 编码）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    # 设置控制台编码为 UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    root_logger.addHandler(console_handler)
    
    logger = logging.getLogger(__name__)
    
    # 每次启动都输出版本信息
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"{APP_NAME} v{APP_VERSION}")
    logger.info("后端服务器启动")
    logger.info(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Python 版本: {sys.version.split()[0]}")
    logger.info(f"工作目录: {current_dir}")
    logger.info(f"日志目录: {logs_dir}")
    logger.info(f"日志文件: {log_file}")
    logger.info(f"可执行文件: {sys.executable}")
    logger.info(f"是否打包: {getattr(sys, 'frozen', False)}")
    logger.info("=" * 60)
    
    return logger

if __name__ == "__main__":
    try:
        # 设置日志
        logger = setup_logging()
        
        # 确保在正确的目录下运行
        if getattr(sys, 'frozen', False):
            # 如果是打包后的 exe
            exe_dir = os.path.dirname(sys.executable)
            logger.info(f"切换到 EXE 目录: {exe_dir}")
            os.chdir(exe_dir)
        
        # 检查数据库文件
        db_file = "database.db"
        if os.path.exists(db_file):
            logger.info(f"[OK] 数据库文件存在: {db_file}")
            logger.info(f"     文件大小: {os.path.getsize(db_file)} 字节")
            
            # 自动数据库迁移（静默升级）
            logger.info("检查数据库结构...")
            try:
                if auto_migrate_on_startup(db_file):
                    logger.info("数据库检查完成")
                else:
                    logger.warning("数据库迁移有问题，但继续启动...")
            except Exception as e:
                logger.warning(f"数据库迁移检查失败: {e}")
                logger.warning("继续启动服务器...")
        else:
            logger.warning(f"[WARN] 数据库文件不存在: {db_file}")
        
        # 检查主应用文件
        main_file = "main.py"
        if os.path.exists(main_file):
            logger.info(f"[OK] 主应用文件存在: {main_file}")
        else:
            logger.warning(f"[WARN] 主应用文件不存在: {main_file}")
        
        logger.info("启动 Uvicorn 服务器...")
        logger.info("监听地址: 127.0.0.1:8000")
        
        # 启动 Uvicorn 服务器
        uvicorn.run(
            "main:app",
            host="127.0.0.1",
            port=8030,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error("=" * 60)
        logger.error("启动失败！")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误信息: {str(e)}")
        logger.error("=" * 60)
        import traceback
        logger.error(traceback.format_exc())
        
        # 保持窗口打开以便查看错误
        input("按回车键退出...")
