"""
简洁版 Web 服务器
启动后端 + 提供前端静态文件 + 自动打开浏览器
"""
import sys
import os
import time
import threading
import webbrowser
import traceback
import logging
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
            webbrowser.open(url)
            print(f"✓ 浏览器已打开: {url}")
        except Exception as e:
            print(f"打开浏览器失败: {e}")
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
        host = "127.0.0.1"
        
        # 查找可用端口
        logger.info("正在查找可用端口...")
        port = find_available_port(start_port=8000, max_attempts=10)
        
        if port is None:
            logger.error("无法找到可用端口（尝试了 8000-8009）")
            logger.error("请关闭占用这些端口的程序后重试")
            input("按回车键退出...")
            sys.exit(1)
        
        if port != 8000:
            logger.warning(f"端口 8000 被占用，使用端口 {port}")
        else:
            logger.info(f"使用默认端口 {port}")
        
        url = f"http://{host}:{port}"
        
        logger.info(f"🚀 启动服务器: {url}")
        logger.info(f"📁 前端目录: {frontend_dir}")
        logger.info(f"📊 数据库: database.db")
        logger.info("⏳ 浏览器将在 3 秒后自动打开...")
        logger.info("提示：按 Ctrl+C 可以停止服务器")
        logger.info("=" * 60)
        
        # 延迟打开浏览器
        open_browser_delayed(url, delay=3)
        
        # 启动服务器
        uvicorn.run(
            app,  # 直接传入 app 对象
            host=host,
            port=port,
            log_level="info",
            access_log=True,  # 启用访问日志
            reload=False
        )
        
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
        input("按回车键退出...")
        sys.exit(1)

if __name__ == "__main__":
    main()