"""
后端服务器启动脚本
用于 PyInstaller 打包后的独立运行
"""
import uvicorn
import sys
import os
import logging
from datetime import datetime

# 应用版本号
APP_VERSION = "2.1.0"
APP_NAME = "眼科注射预约系统后端"

# 配置日志
def setup_logging():
    # 获取当前工作目录
    current_dir = os.getcwd()
    
    # 日志文件在上级目录的 logs 文件夹
    if getattr(sys, 'frozen', False):
        # 打包后：当前目录是 backend/，日志在 ../logs/
        logs_dir = os.path.join(os.path.dirname(current_dir), "logs")
    else:
        # 开发环境：直接在当前目录
        logs_dir = "logs"
    
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
            port=8000,
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
