"""
支持静态文件服务的 FastAPI 应用
用于 Web 版本打包
"""
import os
import sqlite3
import logging
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.exceptions import HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from database import create_db_and_tables, engine
from routers import patients_router, appointments_router, data_dictionary_router
from routers.system_settings import router as system_settings_router
from routers.follow_ups import router as follow_ups_router
from routers.dashboard import router as dashboard_router
from routers.auth import router as auth_router
from models.user import User
from sqlmodel import Session, select
from security import get_password_hash

# 配置日志
logger = logging.getLogger(__name__)

app = FastAPI(title="眼科注射预约系统", version="2.1.3-web")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# 注册 API 路由（必须在静态文件路由之前）
app.include_router(patients_router, prefix="/api")
app.include_router(appointments_router, prefix="/api")
app.include_router(data_dictionary_router, prefix="/api")
app.include_router(system_settings_router, prefix="/api")
app.include_router(follow_ups_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(auth_router, prefix="/api")

# 健康检查（在静态文件路由之前）
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.2.3-web"}

# 静态文件服务
frontend_dir = "frontend"
if os.path.exists(frontend_dir):
    # 挂载 assets 目录
    app.mount("/assets", StaticFiles(directory=f"{frontend_dir}/assets"), name="assets")
    
    # 根路径返回 index.html
    @app.get("/")
    async def read_root():
        return FileResponse(f"{frontend_dir}/index.html")
    
    # 提供根目录的静态文件（logo.png, print-template.png 等）
    @app.get("/{filename}")
    async def serve_static_files(filename: str):
        # 只处理静态文件
        static_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', 
                           '.woff', '.woff2', '.ttf', '.eot', '.json', '.xml', '.txt']
        if any(filename.endswith(ext) for ext in static_extensions):
            file_path = os.path.join(frontend_dir, filename)
            if os.path.exists(file_path):
                return FileResponse(file_path)
        
        # 不是静态文件，返回 index.html（SPA 路由）
        return FileResponse(f"{frontend_dir}/index.html")
    
    # SPA 404 处理：对于非 API 请求的 404，返回 index.html
    @app.exception_handler(404)
    async def custom_404_handler(request: Request, exc):
        # 如果是 API 请求，返回 JSON 错误
        if request.url.path.startswith("/api/"):
            return {"detail": "Not Found"}
        
        # 否则返回 index.html（让前端路由处理）
        return FileResponse(f"{frontend_dir}/index.html")
else:
    @app.get("/")
    async def read_root():
        return {
            "error": "前端文件目录不存在",
            "message": "请确保 frontend 目录与程序在同一目录下"
        }

@app.on_event("startup")
def on_startup():
    """应用启动时执行"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("🚀 眼科注射预约系统 v2.2.3 启动中...")
    logger.info("=" * 60)
    
    # 创建数据库表
    create_db_and_tables()
    
    # 使用新的数据库兼容性处理模块
    from database_compatibility import ensure_database_compatibility
    
    db_path = "database.db"
    if os.path.exists(db_path):
        logger.info("🔍 正在进行数据库兼容性检查...")
        success = ensure_database_compatibility(db_path)
        if not success:
            logger.error("❌ 数据库兼容性检查失败，系统可能无法正常工作")
        else:
            logger.info("✅ 数据库兼容性检查完成")
    else:
        logger.info("📝 创建新数据库...")
    
    logger.info("=" * 60)
    
    # ==================== 2. 密码格式迁移 ====================
    logger.info("=" * 60)
    logger.info("检查密码格式...")
    logger.info("=" * 60)
    
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        
        bcrypt_users = []
        for user in users:
            if user.hashed_password.startswith('$2b$') or user.hashed_password.startswith('$2a$'):
                bcrypt_users.append(user)
        
        if bcrypt_users:
            logger.warning(f"发现 {len(bcrypt_users)} 个用户使用旧密码格式（bcrypt）")
            logger.info("正在自动迁移到新格式（PBKDF2）...")
            
            # 备份数据库
            try:
                backup_file = f"database_password_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                shutil.copy2("database.db", backup_file)
                logger.info(f"✓ 已备份数据库: {backup_file}")
            except Exception as e:
                logger.warning(f"备份失败: {e}")
            
            # 迁移密码 - 统一重置为 admin
            default_password = "admin"
            new_hash = get_password_hash(default_password)
            
            migrated_count = 0
            for user in bcrypt_users:
                try:
                    db_user = session.exec(select(User).where(User.id == user.id)).first()
                    if db_user:
                        db_user.hashed_password = new_hash
                        session.add(db_user)
                        migrated_count += 1
                        logger.info(f"  ✓ {db_user.username} - 密码已重置为: {default_password}")
                except Exception as e:
                    logger.error(f"  ✗ {user.username} - 迁移失败: {e}")
            
            session.commit()
            
            logger.info(f"✓ 已迁移 {migrated_count}/{len(bcrypt_users)} 个用户")
            logger.warning(f"所有迁移用户的密码已重置为: {default_password}")
            logger.info("   请通知用户使用新密码登录")
        else:
            logger.info("✓ 所有用户密码格式正常")
    
    logger.info("=" * 60)
    
    # ==================== 3. 创建默认管理员 ====================
    # 创建默认管理员用户（如果不存在）
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == "admin")).first()
        if not user:
            # 使用 PBKDF2 格式创建密码
            admin_hash = get_password_hash("admin")
            
            admin_user = User(
                username="admin",
                hashed_password=admin_hash,
                is_active=True
            )
            session.add(admin_user)
            session.commit()
            logger.info("✓ 默认用户已创建 (admin/admin)")
        else:
            logger.info("✓ 管理员用户已存在")
    
    # ==================== 4. 初始化系统配置 ====================
    logger.info("=" * 60)
    logger.info("检查系统配置...")
    logger.info("=" * 60)
    
    from models.system_setting import SystemSetting
    
    with Session(engine) as session:
        # 定义默认配置
        default_settings = [
            ('injection_interval_first_4', '30', '前4针注射间隔（天）'),
            ('print_phone_number', '', '打印页面显示的联系电话'),
        ]
        
        for key, value, description in default_settings:
            setting = session.exec(select(SystemSetting).where(SystemSetting.key == key)).first()
            if not setting:
                new_setting = SystemSetting(key=key, value=value, description=description)
                session.add(new_setting)
                logger.info(f"  ✓ 添加配置: {key} = {value}")
        
        session.commit()
        logger.info("✓ 系统配置检查完成")
    
    logger.info("✅ 系统启动完成")
    logger.info("")

@app.on_event("shutdown")
def on_shutdown():
    """应用关闭时执行"""
    logger.info("👋 系统已关闭")