"""
支持静态文件服务的 FastAPI 应用
用于 Web 版本打包
"""
import os
import shutil
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from database import create_db_and_tables, engine
from routers import patients_router, appointments_router, data_dictionary_router
from routers.system_settings import router as system_settings_router
from routers.follow_ups import router as follow_ups_router
from routers.dashboard import router as dashboard_router
from routers.auth import router as auth_router
from models.user import User
from sqlmodel import Session, select
from security import get_password_hash

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # ===== startup =====
    logger.info("=" * 60)
    logger.info("眼科注射预约系统 v2.2.3 启动中...")
    logger.info("=" * 60)

    create_db_and_tables()

    from database_compatibility import ensure_database_compatibility
    db_path = "database.db"
    if os.path.exists(db_path):
        logger.info("正在进行数据库兼容性检查...")
        success = ensure_database_compatibility(db_path)
        if not success:
            logger.error("数据库兼容性检查失败，系统可能无法正常工作")
        else:
            logger.info("数据库兼容性检查完成")

    # 密码格式迁移（bcrypt -> PBKDF2）
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        bcrypt_users = [u for u in users if u.hashed_password.startswith('$2b') or u.hashed_password.startswith('$2a')]

        if bcrypt_users:
            logger.warning(f"发现 {len(bcrypt_users)} 个用户使用旧密码格式，正在迁移...")
            try:
                backup_file = f"database_password_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                shutil.copy2("database.db", backup_file)
                logger.info(f"已备份数据库: {backup_file}")
            except Exception as e:
                logger.warning(f"备份失败: {e}")

            new_hash = get_password_hash("admin")
            for user in bcrypt_users:
                try:
                    db_user = session.exec(select(User).where(User.id == user.id)).first()
                    if db_user:
                        db_user.hashed_password = new_hash
                        session.add(db_user)
                        logger.info(f"  {db_user.username} 密码已重置为: admin")
                except Exception as e:
                    logger.error(f"  {user.username} 迁移失败: {e}")
            session.commit()
        else:
            logger.info("所有用户密码格式正常")

    # 创建默认管理员
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == "admin")).first()
        if not user:
            admin_user = User(username="admin", hashed_password=get_password_hash("admin"), is_active=True)
            session.add(admin_user)
            session.commit()
            logger.info("默认用户已创建 (admin/admin)")
        else:
            logger.info("管理员用户已存在")

    # 初始化系统配置
    from models.system_setting import SystemSetting
    with Session(engine) as session:
        default_settings = [
            ('injection_interval_first_4', '30', '前4针注射间隔（天）'),
            ('print_phone_number', '', '打印页面显示的联系电话'),
        ]
        for key, value, description in default_settings:
            setting = session.exec(select(SystemSetting).where(SystemSetting.key == key)).first()
            if not setting:
                session.add(SystemSetting(key=key, value=value, description=description))
                logger.info(f"  添加配置: {key} = {value}")
        session.commit()

    logger.info("系统启动完成")
    logger.info("=" * 60)

    yield

    # ===== shutdown =====
    logger.info("系统已关闭")


app = FastAPI(title="眼科注射预约系统", version="2.2.3-web", lifespan=lifespan)

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


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.2.3-web"}


# 静态文件服务
frontend_dir = "frontend"
if os.path.exists(frontend_dir):
    app.mount("/assets", StaticFiles(directory=f"{frontend_dir}/assets"), name="assets")

    @app.get("/")
    async def read_root():
        return FileResponse(f"{frontend_dir}/index.html")

    @app.get("/{filename}")
    async def serve_static_files(filename: str):
        static_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
                              '.woff', '.woff2', '.ttf', '.eot', '.json', '.xml', '.txt']
        if any(filename.endswith(ext) for ext in static_extensions):
            file_path = os.path.join(frontend_dir, filename)
            if os.path.exists(file_path):
                return FileResponse(file_path)
        return FileResponse(f"{frontend_dir}/index.html")

    @app.exception_handler(404)
    async def custom_404_handler(request: Request, exc):
        if request.url.path.startswith("/api/"):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})
        return FileResponse(f"{frontend_dir}/index.html")

else:
    @app.get("/")
    async def read_root():
        return {"error": "前端文件目录不存在", "message": "请确保 frontend 目录与程序在同一目录下"}


if __name__ == "__main__":
    import uvicorn
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("logs/backend.log", encoding="utf-8"),
        ]
    )
    os.makedirs("logs", exist_ok=True)
    uvicorn.run(app, host="0.0.0.0", port=8031)
