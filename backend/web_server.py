"""
Web版本后端服务器启动脚本
自动打开浏览器，提供完整的Web体验
"""
import uvicorn
import sys
import os
import logging
import sqlite3
import shutil
import webbrowser
import threading
import time
from datetime import datetime

# 应用版本号
APP_VERSION = "2.1.3-web"
APP_NAME = "眼科注射预约系统 Web版"

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
        sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        cursor.execute(sql)
        logging.info(f"✓ 添加字段: {table_name}.{column_name} ({description})")
        return True
    except Exception as e:
        logging.error(f"✗ 添加字段失败 {table_name}.{column_name}: {e}")
        return False

def auto_migrate_database():
    """自动执行数据库迁移"""
    db_path = "database.db"
    
    if not os.path.exists(db_path):
        logging.warning("数据库文件不存在，将在首次启动时创建")
        return True
    
    logging.info("开始检查数据库结构...")
    
    # 备份数据库
    backup_database_silent(db_path)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 需要添加的字段列表
        migrations = [
            # 患者表新增字段
            ("patients", "medical_card_number", "TEXT", "医保卡号"),
            
            # 预约表新增字段  
            ("appointments", "attending_doctor", "TEXT", "主治医生"),
            ("appointments", "virus_report", "TEXT", "病毒检测报告"),
            ("appointments", "blood_sugar", "TEXT", "血糖"),
            ("appointments", "blood_pressure", "TEXT", "血压"),
            ("appointments", "left_eye_pressure", "TEXT", "左眼眼压"),
            ("appointments", "right_eye_pressure", "TEXT", "右眼眼压"),
            ("appointments", "eye_wash_result", "TEXT", "洗眼结果"),
        ]
        
        added_count = 0
        for table_name, column_name, column_type, description in migrations:
            if add_column_safe_exec(cursor, table_name, column_name, column_type, description):
                added_count += 1
        
        conn.commit()
        conn.close()
        
        if added_count > 0:
            logging.info(f"数据库迁移完成，新增 {added_count} 个字段")
        else:
            logging.info("数据库结构已是最新，无需迁移")
        
        return True
        
    except Exception as e:
        logging.error(f"数据库迁移失败: {e}")
        return False

# ==================== 浏览器自动打开功能 ====================

def wait_for_server(host, port, timeout=30):
    """等待服务器启动"""
    import socket
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                return True
        except:
            pass
        
        time.sleep(0.5)
    
    return False

def open_browser_delayed(url, delay=3):
    """延迟打开浏览器"""
    def open_browser():
        time.sleep(delay)
        
        # 等待服务器启动
        if wait_for_server("127.0.0.1", 8000, timeout=10):
            logging.info(f"正在打开浏览器: {url}")
            try:
                webbrowser.open(url)
                logging.info("✓ 浏览器已打开")
            except Exception as e:
                logging.error(f"打开浏览器失败: {e}")
                print(f"\n请手动打开浏览器访问: {url}")
        else:
            logging.error("服务器启动超时，请手动访问")
            print(f"\n服务器启动可能需要更多时间，请稍后手动访问: {url}")
    
    # 在后台线程中打开浏览器
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

# ==================== 主程序 ====================

def setup_logging():
    """设置日志"""
    # 创建logs目录
    os.makedirs("logs", exist_ok=True)
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/web_server.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """主函数"""
    setup_logging()
    
    print("=" * 60)
    print(f"  {APP_NAME}")
    print(f"  版本: {APP_VERSION}")
    print(f"  启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 执行数据库迁移
    logging.info("执行数据库迁移...")
    if not auto_migrate_database():
        logging.error("数据库迁移失败，程序退出")
        input("按回车键退出...")
        sys.exit(1)
    
    # 设置静态文件目录
    static_dir = os.path.join(os.path.dirname(__file__), "frontend")
    if not os.path.exists(static_dir):
        logging.error(f"前端文件目录不存在: {static_dir}")
        print(f"\n错误：找不到前端文件目录")
        print(f"请确保 'frontend' 目录存在于程序同级目录")
        input("按回车键退出...")
        sys.exit(1)
    
    # 服务器配置
    host = "127.0.0.1"
    port = 8000
    url = f"http://{host}:{port}"
    
    print(f"\n🚀 启动服务器...")
    print(f"📍 访问地址: {url}")
    print(f"📁 静态文件: {static_dir}")
    print(f"📊 数据库: database.db")
    print(f"📝 日志文件: logs/web_server.log")
    print("\n⏳ 正在启动服务器，请稍候...")
    
    # 延迟打开浏览器
    open_browser_delayed(url, delay=2)
    
    try:
        # 启动服务器
        uvicorn.run(
            "main_web:app",  # 使用 Web 版本的应用
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            reload=False
        )
    except KeyboardInterrupt:
        logging.info("服务器已停止")
        print("\n👋 服务器已停止")
    except Exception as e:
        logging.error(f"服务器启动失败: {e}")
        print(f"\n❌ 服务器启动失败: {e}")
        input("按回车键退出...")
        sys.exit(1)

if __name__ == "__main__":
    main()