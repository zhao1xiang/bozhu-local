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
import mimetypes
from datetime import datetime

def setup_logging():
    """配置日志系统"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_filename = os.path.join(log_dir, f"server_{datetime.now().strftime('%Y%m%d')}.log")
    
    log_format = '%(asctime)s [%(levelname)s] %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("日志系统已启动")
    logger.info(f"日志文件: {log_filename}")
    logger.info("=" * 60)
    
    return logger

def open_browser_delayed(url, delay=5):
    """延迟打开浏览器"""
    def open_browser():
        time.sleep(delay)
        try:
            import socket
            max_retries = 10
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex(('127.0.0.1', 38125))
                    sock.close()
                    
                    if result == 0:
                        webbrowser.open(url)
                        print(f"浏览器已打开: {url}")
                        return
                    else:
                        retry_count += 1
                        time.sleep(1)
                except Exception:
                    retry_count += 1
                    time.sleep(1)
            
            print(f"请手动打开浏览器访问: {url}")
            
        except Exception as e:
            print(f"打开浏览器失败: {e}")
    
    threading.Thread(target=open_browser, daemon=True).start()

def main():
    """主函数"""
    logger = setup_logging()
    
    try:
        logger.info("=" * 60)
        logger.info("眼科注射预约系统 Web版")
        logger.info("正在启动...")
        logger.info("=" * 60)
        
        logger.info(f"当前目录: {os.getcwd()}")
        
        # 检查前端文件
        frontend_dir = "frontend"
        if not os.path.exists(frontend_dir):
            logger.error(f"找不到前端文件目录 '{frontend_dir}'")
            sys.exit(1)
        
        logger.info(f"找到前端目录: {frontend_dir}")
        
        # 执行数据库迁移（添加新字段）- 必须在导入 main 之前执行
        try:
            logger.info("=" * 60)
            logger.info("开始自动数据库迁移检查...")
            logger.info("=" * 60)
            
            # 直接在这里执行迁移，确保使用正确的数据库路径
            import sqlite3
            db_path = os.path.join(os.getcwd(), "database.db")
            logger.info(f"数据库路径: {db_path}")
            
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # 检查并添加缺失的列
                migrations = {
                    'patient': [
                        ('outpatient_number', 'VARCHAR', '门诊号'),
                        ('medical_card_number', 'VARCHAR', '就诊卡号'),
                        ('phone', 'VARCHAR', '手机号'),
                        ('diagnosis', 'VARCHAR', '诊断'),
                        ('diagnosis_other', 'VARCHAR', '诊断其他说明'),
                        ('drug_type', 'VARCHAR', '药物类型'),
                        ('drug_type_other', 'VARCHAR', '药物其他说明'),
                        ('left_vision', 'VARCHAR', '左眼裸眼视力'),
                        ('right_vision', 'VARCHAR', '右眼裸眼视力'),
                        ('left_vision_corrected', 'VARCHAR', '左眼矫正视力'),
                        ('right_vision_corrected', 'VARCHAR', '右眼矫正视力'),
                        ('left_eye', 'BOOLEAN DEFAULT 0', '左眼'),
                        ('right_eye', 'BOOLEAN DEFAULT 0', '右眼'),
                        ('patient_type', 'VARCHAR', '患者类型'),
                        ('injection_count', 'INTEGER', '已完成针数'),
                        ('remarks', 'TEXT', '备注'),
                        ('status', 'VARCHAR DEFAULT "active"', '状态'),
                        ('is_deleted', 'BOOLEAN DEFAULT 0', '软删除标记'),
                        ('doctor', 'VARCHAR', '归属医生'),
                        ('created_at', 'DATETIME', '创建时间'),
                        ('updated_at', 'DATETIME', '更新时间'),
                    ],
                    'appointment': [
                        ('appointment_date', 'DATE', '预约日期'),
                        ('time_slot', 'VARCHAR', '时间段'),
                        ('status', 'VARCHAR DEFAULT "scheduled"', '状态'),
                        ('notes', 'TEXT', '备注'),
                        ('source', 'VARCHAR', '来源'),
                        ('is_deleted', 'BOOLEAN DEFAULT 0', '软删除标记'),
                        ('injection_number', 'VARCHAR', '注药号'),
                        ('injection_count', 'INTEGER', '注药次数'),
                        ('eye', 'VARCHAR', '眼别'),
                        ('drug_name', 'VARCHAR', '药品名称'),
                        ('drug_name_other', 'VARCHAR', '药品其他说明'),
                        ('cost_type', 'VARCHAR', '费别'),
                        ('doctor', 'VARCHAR', '注药医生'),
                        ('attending_doctor', 'VARCHAR', '管床医生'),
                        ('virus_report', 'VARCHAR', '病毒报告'),
                        ('blood_sugar', 'VARCHAR', '血糖'),
                        ('blood_pressure', 'VARCHAR', '血压'),
                        ('left_eye_pressure', 'VARCHAR', '左眼压'),
                        ('right_eye_pressure', 'VARCHAR', '右眼压'),
                        ('eye_wash_result', 'VARCHAR', '冲眼结果'),
                        ('follow_up_date', 'DATE', '复诊时间'),
                        ('next_follow_up_date', 'DATE', '下次复诊时间'),
                        ('diagnosis', 'VARCHAR', '诊断'),
                        ('pre_op_vision_left', 'VARCHAR', '左眼术前裸眼视力'),
                        ('pre_op_vision_right', 'VARCHAR', '右眼术前裸眼视力'),
                        ('pre_op_vision_left_corrected', 'VARCHAR', '左眼术前矫正视力'),
                        ('pre_op_vision_right_corrected', 'VARCHAR', '右眼术前矫正视力'),
                        ('treatment_phase', 'VARCHAR', '治疗周期'),
                        ('condition_status', 'VARCHAR', '状况'),
                        ('created_at', 'DATETIME', '创建时间'),
                        ('updated_at', 'DATETIME', '更新时间'),
                    ],
                    'user': [
                        ('is_active', 'BOOLEAN DEFAULT 1', '是否激活'),
                        ('role', 'VARCHAR DEFAULT "admin"', '用户角色'),
                        ('doctor', 'VARCHAR', '绑定医生'),
                        ('wards', 'VARCHAR', '分组'),
                    ],
                    'data_dictionary': [
                        ('category', 'VARCHAR', '分类'),
                        ('value', 'VARCHAR', '值'),
                        ('label', 'VARCHAR', '显示名称'),
                        ('sort_order', 'INTEGER DEFAULT 0', '排序'),
                        ('is_active', 'BOOLEAN DEFAULT 1', '是否启用'),
                        ('extra', 'VARCHAR', '扩展字段'),
                        ('ward', 'VARCHAR', '病区'),
                        ('created_at', 'DATETIME', '创建时间'),
                    ],
                }
                
                changes = 0
                for table_name, fields in migrations.items():
                    for col_name, col_type, description in fields:
                        try:
                            # 检查列是否存在
                            cursor.execute(f"PRAGMA table_info({table_name})")
                            columns = [row[1] for row in cursor.fetchall()]
                            
                            if col_name not in columns:
                                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")
                                logger.info(f"✓ 添加字段: {table_name}.{col_name} ({description})")
                                changes += 1
                        except Exception as e:
                            logger.warning(f"添加字段 {table_name}.{col_name} 失败: {e}")
                
                conn.commit()
                conn.close()
                
                if changes > 0:
                    logger.info(f"✓ 数据库迁移完成，新增 {changes} 个字段")
                else:
                    logger.info("✓ 数据库已是最新")
            else:
                logger.warning(f"数据库文件不存在: {db_path}")
            
            logger.info("=" * 60)
        except Exception as e:
            logger.error(f"数据库迁移异常: {e}")
            import traceback
            logger.error(traceback.format_exc())
            logger.warning("继续启动应用...")
        
        # 导入模块
        logger.info("正在加载模块...")
        try:
            import uvicorn
            logger.info("uvicorn 模块加载成功")
        except ImportError as e:
            logger.error(f"无法加载 uvicorn: {e}")
            sys.exit(1)
        
        try:
            from main import app
            logger.info("main 模块加载成功")
        except ImportError as e:
            logger.error(f"无法加载 main: {e}")
            logger.error(traceback.format_exc())
            sys.exit(1)
        
        # 挂载静态文件 - 只挂载 assets 目录，避免拦截 API 路由
        # SPA 的 HTML 页面通过单独的路由处理
        from fastapi.responses import FileResponse, PlainTextResponse
        mimetypes.add_type("application/javascript; charset=utf-8", ".js")
        mimetypes.add_type("text/css; charset=utf-8", ".css")
        mimetypes.add_type("application/json; charset=utf-8", ".json")
        mimetypes.add_type("image/svg+xml", ".svg")
        
        assets_dir = os.path.join(frontend_dir, "assets")
        if os.path.exists(assets_dir):
            @app.get("/assets/{asset_path:path}")
            async def serve_asset(asset_path: str):
                assets_root = os.path.abspath(assets_dir)
                file_path = os.path.abspath(os.path.join(assets_dir, asset_path))
                if not file_path.startswith(assets_root + os.sep) or not os.path.isfile(file_path):
                    logger.warning(f"静态资源不存在: /assets/{asset_path} -> {file_path}")
                    return PlainTextResponse("Asset not found", status_code=404)

                suffix = os.path.splitext(file_path)[1].lower()
                media_types = {
                    ".js": "application/javascript; charset=utf-8",
                    ".mjs": "application/javascript; charset=utf-8",
                    ".css": "text/css; charset=utf-8",
                    ".map": "application/json; charset=utf-8",
                    ".json": "application/json; charset=utf-8",
                    ".svg": "image/svg+xml",
                    ".png": "image/png",
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".webp": "image/webp",
                    ".woff": "font/woff",
                    ".woff2": "font/woff2",
                }
                return FileResponse(file_path, media_type=media_types.get(suffix))

            logger.info(f"静态资源已挂载: /assets -> {assets_dir}")
        
        # 为前端静态文件（非 assets）添加路由
        from starlette.requests import Request as StarletteRequest
        
        @app.get("/{static_path:path}")
        async def serve_frontend_static_or_spa(static_path: str):
            static_root = os.path.abspath(frontend_dir)
            file_path = os.path.abspath(os.path.join(frontend_dir, static_path))
            if (
                static_path
                and not static_path.startswith(("api/", "app/", "embed/", "assets/"))
                and file_path.startswith(static_root + os.sep)
                and os.path.isfile(file_path)
            ):
                suffix = os.path.splitext(file_path)[1].lower()
                media_types = {
                    ".html": "text/html; charset=utf-8",
                    ".png": "image/png",
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".svg": "image/svg+xml",
                    ".webp": "image/webp",
                    ".gif": "image/gif",
                    ".ico": "image/x-icon",
                    ".css": "text/css; charset=utf-8",
                    ".js": "application/javascript; charset=utf-8",
                    ".json": "application/json; charset=utf-8",
                    ".woff": "font/woff",
                    ".woff2": "font/woff2",
                }
                return FileResponse(file_path, media_type=media_types.get(suffix))
            return FileResponse(os.path.join(frontend_dir, "index.html"), media_type="text/html")
        
        # 所有非 API 路由返回 index.html（SPA 路由）
        @app.get("/")
        async def serve_index():
            return FileResponse(os.path.join(frontend_dir, "index.html"), media_type="text/html")
        
        @app.get("/app/{full_path:path}")
        async def serve_spa(full_path: str):
            return FileResponse(os.path.join(frontend_dir, "index.html"), media_type="text/html")
        
        @app.get("/embed/{full_path:path}")
        async def serve_embed_spa(full_path: str):
            return FileResponse(os.path.join(frontend_dir, "index.html"), media_type="text/html")
        
        logger.info(f"前端 SPA 路由已配置")
        
        # 服务器配置
        host = "0.0.0.0"
        port = 38125
        url = f"http://127.0.0.1:{port}"
        
        # 检查端口是否被占用
        import socket as _socket
        try:
            _test_sock = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
            _test_sock.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, 1)
            _test_sock.bind(("0.0.0.0", port))
            _test_sock.close()
        except OSError:
            logger.error(f"端口 {port} 已被占用！")
            logger.error("请关闭已运行的程序实例后再启动。")
            logger.error("如需强制启动，请在任务管理器中结束 backend_server.exe 进程。")
            import time as _time
            _time.sleep(10)  # 等待用户看到错误信息
            sys.exit(1)
        
        logger.info(f"准备启动服务器: {url}")
        logger.info("=" * 60)
        
        # 打开浏览器
        open_browser_delayed(url, delay=5)
        
        # 启动服务器
        logger.info("正在启动后端服务...")
        
        import uvicorn.config
        import uvicorn.server
        
        config = uvicorn.Config(
            app=app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
        )
        
        server = uvicorn.Server(config)
        
        # PyInstaller 打包环境下需要用 asyncio.run 启动，避免 loop 参数冲突
        import asyncio
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(server.serve())
        
    except KeyboardInterrupt:
        logger.info("服务器已停止")
    except Exception as e:
        logger.error(f"错误: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    main()
