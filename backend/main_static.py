"""
主应用程序 - 包含静态文件服务
用于服务器部署的 Web 服务器
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pathlib import Path
from database import create_db_and_tables
from routers import patients_router, appointments_router, data_dictionary_router, system_settings, follow_ups, dashboard, auth
from routers import users as users_router
from models.user import User
from models.system_setting import SystemSetting
from security import get_password_hash
from sqlmodel import Session, select
from database import engine

# 获取前端目录
script_dir = Path(__file__).parent
frontend_dir = script_dir / "frontend"

print(f"[Frontend] 脚本目录: {script_dir}")
print(f"[Frontend] 前端目录: {frontend_dir}")
print(f"[Frontend] 前端目录存在: {frontend_dir.exists()}")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

@app.on_event("startup")
def on_startup():
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Creating database tables...")
        create_db_and_tables()
        logger.info("Database tables created")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return
    
    try:
        logger.info("Running database migrations...")
        from auto_migrate import check_and_migrate
        if check_and_migrate():
            logger.info("Database migrations completed successfully")
        else:
            logger.warning("Database migrations completed with warnings")
    except Exception as e:
        logger.error(f"Failed to run database migrations: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    try:
        with Session(engine) as session:
            user = session.exec(select(User).where(User.username == "admin")).first()
            if not user:
                admin_user = User(username="admin", hashed_password=get_password_hash("admin"))
                session.add(admin_user)
                session.commit()
                logger.info("Default admin user created.")
            
            default_settings = [
                ('reminder_days_advance', '3', '提前提醒天数'),
                ('injection_weekday', '1', '玻注日（1-7 表示周一到周日，可多选，逗号分隔）'),
                ('injection_interval_first_4', '30', '前4针注射间隔（天）'),
                ('print_phone_number', '', '打印页面显示的联系电话'),
            ]
            for key, default_value, description in default_settings:
                setting = session.exec(select(SystemSetting).where(SystemSetting.key == key)).first()
                if not setting:
                    new_setting = SystemSetting(key=key, value=default_value, description=description)
                    session.add(new_setting)
                    logger.info(f"Created default system setting: {key} = {default_value}")
            session.commit()
            logger.info("Startup completed successfully")
    except Exception as e:
        logger.error(f"Failed to initialize admin/settings: {e}")
        import traceback
        logger.error(traceback.format_exc())

# ===== API 路由 =====
app.include_router(patients_router, prefix="/api")
app.include_router(appointments_router, prefix="/api")
app.include_router(data_dictionary_router, prefix="/api")
app.include_router(system_settings.router, prefix="/api")
app.include_router(follow_ups.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users_router.router, prefix="/api")

from routers.embed import router as embed_router
app.include_router(embed_router, prefix="/api")

@app.options("/api/health")
@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Backend is ready"}

# ===== 前端静态文件路由（手动处理，避免 mount 拦截 API）=====
if frontend_dir.exists():
    # 挂载 assets 目录
    assets_dir = frontend_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
        print(f"[Frontend] /assets 已挂载")

    # 根路径返回 index.html
    @app.get("/")
    async def serve_index():
        return FileResponse(frontend_dir / "index.html")

    # /app/* 路由返回 index.html（SPA 路由）
    @app.get("/app/{full_path:path}")
    async def serve_app(full_path: str):
        return FileResponse(frontend_dir / "index.html")

    # 其他静态文件（logo.png, favicon.svg 等）
    @app.get("/{filename}")
    async def serve_static_file(filename: str):
        file_path = frontend_dir / filename
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        # 不是文件，返回 index.html
        return FileResponse(frontend_dir / "index.html")

    print(f"[Frontend] 前端路由已配置")
else:
    print(f"[Frontend] 前端目录不存在，跳过")
