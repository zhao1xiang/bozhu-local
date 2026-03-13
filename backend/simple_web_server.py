"""
简洁版 Web 服务器
启动后端 + 提供前端静态文件 + 自动打开浏览器
包含自动数据库迁移功能
"""
import sys
import os
import time
import threading
import webbrowser
import traceback
import logging
import sqlite3
import shutil
from datetime import datetime

def setup_logging():
    """配置日志系统"""
    # 创建 logs 目录
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 日志文件名：包含日期
    log_filename = os.path.join(log_dir, f"server_{datetime.now().strftime('%Y%m%d')}.log")
    
    # 配置日志格式
    log_format = '%(asctime)s [%(levelname)s] %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # 配置根日志记录器
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            # 文件处理器
            logging.FileHandler(log_filename, encoding='utf-8'),
            # 控制台处理器
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # 获取日志记录器
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("日志系统已启动")
    logger.info(f"日志文件: {log_filename}")
    logger.info("=" * 60)
    
    return logger

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

def add_column_safe_exec(cursor, table_name, column_name, column_type, default_value="", description=""):
    """安全地添加列（如果不存在）"""
    if column_exists_check(cursor, table_name, column_name):
        logging.debug(f"字段已存在，跳过: {table_name}.{column_name}")
        return False
    
    try:
        if default_value:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} DEFAULT {default_value}")
        else:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
        logging.info(f"✓ 添加字段: {table_name}.{column_name} ({description})")
        return True
    except Exception as e:
        logging.error(f"✗ 添加字段失败 {table_name}.{column_name}: {e}")
        return False

def auto_migrate_on_startup(db_path, logger):
    """启动时自动迁移数据库"""
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
                ('medical_card_number', 'VARCHAR', '', '就诊卡号'),
                ('remarks', 'TEXT', '', '备注'),
                ('is_deleted', 'BOOLEAN', '0', '软删除标记'),
            ],
            'appointment': [
                ('attending_doctor', 'VARCHAR', '', '管床医生'),
                ('virus_report', 'VARCHAR', '', '病毒报告'),
                ('blood_sugar', 'VARCHAR', '', '血糖'),
                ('blood_pressure', 'VARCHAR', '', '血压'),
                ('left_eye_pressure', 'VARCHAR', '', '左眼压'),
                ('right_eye_pressure', 'VARCHAR', '', '右眼压'),
                ('eye_wash_result', 'VARCHAR', '', '冲眼结果'),
                ('time_slot', 'TEXT', '', '时间段'),
            ]
        }
        
        # 检查是否需要迁移
        needs_migration = False
        for table_name, fields in migrations.items():
            for field_info in fields:
                field_name = field_info[0]
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
            for field_info in fields:
                field_name, field_type, default_value, description = field_info
                if add_column_safe_exec(cursor, table_name, field_name, field_type, default_value, description):
                    changes_made += 1
        
        # 提交更改
        conn.commit()
        
        # 验证迁移
        logger.info("验证迁移结果...")
        all_ok = True
        for table_name, fields in migrations.items():
            for field_info in fields:
                field_name = field_info[0]
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
        logger.error(traceback.format_exc())
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        return False

def find_available_port(start_port=8000, max_attempts=10):
    """查找可用端口"""
    import socket
    
    for port in range(start_port, start_port + max_attempts):
        try:
            # 尝试绑定端口
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('127.0.0.1', port))
            sock.close()
            return port
        except OSError:
            # 端口被占用，尝试下一个
            continue
    
    # 如果都被占用，返回 None
    return None

def open_browser_delayed(url, delay=3):
    """延迟打开浏览器"""
    def open_browser():
        time.sleep(delay)
        try:
            # 在打开浏览器前，先检查服务器是否真的启动了
            import socket
            max_retries = 10
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # 尝试连接服务器
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex(('127.0.0.1', int(url.split(':')[-1])))
                    sock.close()
                    
                    if result == 0:
                        # 服务器已启动，打开浏览器
                        webbrowser.open(url)
                        print(f"✓ 浏览器已打开: {url}")
                        return
                    else:
                        # 服务器还没启动，继续等待
                        retry_count += 1
                        time.sleep(1)
                except Exception:
                    retry_count += 1
                    time.sleep(1)
            
            # 超时后仍然尝试打开浏览器
            print(f"⚠ 服务器启动检测超时，仍然尝试打开浏览器: {url}")
            webbrowser.open(url)
            
        except Exception as e:
            print(f"✗ 打开浏览器失败: {e}")
            print(f"请手动打开浏览器访问: {url}")
    
    threading.Thread(target=open_browser, daemon=True).start()

def main():
    """主函数"""
    # 初始化日志
    logger = setup_logging()
    
    try:
        logger.info("=" * 60)
        logger.info("眼科注射预约系统 Web版")
        logger.info("正在启动...")
        logger.info("=" * 60)
        
        # 显示当前工作目录
        logger.info(f"当前目录: {os.getcwd()}")
        logger.info(f"程序目录: {os.path.dirname(os.path.abspath(__file__))}")
        
        # 检查前端文件是否存在
        frontend_dir = "frontend"
        if not os.path.exists(frontend_dir):
            logger.error(f"找不到前端文件目录 '{frontend_dir}'")
            logger.error("请确保 frontend 目录与程序在同一目录下")
            logger.info("当前目录下的文件：")
            for item in os.listdir('.'):
                logger.info(f"  - {item}")
            input("按回车键退出...")
            sys.exit(1)
        
        logger.info(f"✓ 找到前端目录: {frontend_dir}")
        
        # 检查数据库文件
        if os.path.exists("database.db"):
            logger.info(f"✓ 找到数据库文件: database.db")
            
            # 自动数据库迁移
            logger.info("检查数据库结构...")
            try:
                if auto_migrate_on_startup("database.db", logger):
                    logger.info("数据库检查完成")
                else:
                    logger.warning("数据库迁移有问题，但继续启动...")
            except Exception as e:
                logger.warning(f"数据库迁移检查失败: {e}")
                logger.warning("继续启动服务器...")
        else:
            logger.warning(f"未找到数据库文件，将自动创建")
        
        # 导入必要的模块
        logger.info("正在加载模块...")
        try:
            import uvicorn
            logger.info("✓ uvicorn 模块加载成功")
        except ImportError as e:
            logger.error(f"无法加载 uvicorn: {e}")
            input("按回车键退出...")
            sys.exit(1)
        
        try:
            from main_static import app
            logger.info("✓ main_static 模块加载成功")
        except ImportError as e:
            logger.error(f"无法加载 main_static: {e}")
            logger.error("详细错误信息：")
            logger.error(traceback.format_exc())
            input("按回车键退出...")
            sys.exit(1)
        
        # 服务器配置
        host = "0.0.0.0"  # 监听所有网卡，支持局域网访问
        port = 38125  # 固定端口号
        
        logger.info(f"使用固定端口 {port}")
        logger.info(f"监听所有网卡 (0.0.0.0)，支持局域网访问")
        
        # 本地访问地址
        url = f"http://127.0.0.1:{port}"
        
        logger.info(f"🚀 准备启动服务器: {url}")
        logger.info(f"📁 前端目录: {frontend_dir}")
        logger.info(f"📊 数据库: database.db")
        logger.info("⏳ 等待服务器启动完成后自动打开浏览器...")
        logger.info("   （如果浏览器未自动打开，请手动访问上述地址）")
        logger.info("提示：按 Ctrl+C 可以停止服务器")
        logger.info("=" * 60)
        
        # 延迟打开浏览器（会自动检测服务器是否启动）
        open_browser_delayed(url, delay=5)
        
        # 启动服务器
        logger.info(">>> 正在启动后端服务...")
        logger.info(f">>> 监听地址: {host}:{port}")
        
        try:
            # 创建 uvicorn 配置
            import uvicorn.config
            import uvicorn.server
            
            config = uvicorn.Config(
                app=app,
                host=host,
                port=port,
                log_level="info",
                access_log=True,
                loop="asyncio"  # 明确指定事件循环
            )
            
            server = uvicorn.Server(config)
            logger.info(">>> uvicorn Server 已创建，准备启动...")
            server.run()
            
        except Exception as e:
            logger.error(f">>> 后端服务启动失败: {e}")
            logger.error(traceback.format_exc())
            raise
        
    except KeyboardInterrupt:
        logger.info("=" * 60)
        logger.info("👋 服务器已停止（用户中断）")
        logger.info("=" * 60)
    except Exception as e:
        logger.error("=" * 60)
        logger.error("服务器启动失败")
        logger.error("=" * 60)
        logger.error(f"错误信息: {e}")
        logger.error("详细错误信息：")
        logger.error(traceback.format_exc())
        logger.error("=" * 60)
        # PyInstaller 打包后不能使用 input()
        try:
            input("按回车键退出...")
        except:
            time.sleep(10)  # 如果 input() 失败，等待 10 秒
        sys.exit(1)

if __name__ == "__main__":
    # PyInstaller 打包时需要调用 freeze_support()
    import multiprocessing
    multiprocessing.freeze_support()
    
    main()