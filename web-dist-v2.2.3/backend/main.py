from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_db_and_tables
from routers import patients_router, appointments_router, data_dictionary_router, system_settings, follow_ups, dashboard, auth
from models.user import User
from models.system_setting import SystemSetting
from security import get_password_hash
from sqlmodel import Session, select
from database import engine
from contextlib import asynccontextmanager
from database_compatibility import ensure_database_compatibility
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 启动眼科注射预约系统...")
    
    # 数据库兼容性检查和修复
    db_path = "database.db"
    if os.path.exists(db_path):
        logger.info("📋 检查数据库兼容性...")
        if not ensure_database_compatibility(db_path):
            logger.error("❌ 数据库兼容性检查失败，请检查日志")
            # 不退出，尝试继续运行
        else:
            logger.info("✅ 数据库兼容性检查通过")
    
    # 创建数据库表
    create_db_and_tables()
    
    # Create default admin user if not exists
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == "admin")).first()
        if not user:
            # Create admin user
            admin_user = User(username="admin", hashed_password=get_password_hash("admin123"))
            session.add(admin_user)
            session.commit()
            logger.info("👤 默认管理员账号已创建")
        
        # Initialize default system settings if not exists
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
                logger.info(f"⚙️  创建系统设置: {key} = {default_value}")
        
        session.commit()
    
    logger.info("✅ 系统启动完成")
    yield
    # Shutdown (if needed)
    logger.info("🛑 系统正在关闭...")

app = FastAPI(lifespan=lifespan)

# 开发环境允许所有来源，生产环境使用白名单
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:4173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:4173",
    "tauri://localhost",
    "http://tauri.localhost",
    "https://tauri.localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=False,  # 允许所有来源时必须设为False
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

app.include_router(patients_router, prefix="/api")
app.include_router(appointments_router, prefix="/api")

app.include_router(data_dictionary_router, prefix="/api")
app.include_router(system_settings.router, prefix="/api")
app.include_router(follow_ups.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(auth.router, prefix="/api")

@app.get("/fix-admin")
def fix_admin():
    from security import get_password_hash
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == "admin")).first()
        if user:
            user.hashed_password = get_password_hash("admin")
            session.add(user)
            session.commit()
            return {"message": "Admin password reset"}
        else:
            admin_user = User(username="admin", hashed_password=get_password_hash("admin"))
            session.add(admin_user)
            session.commit()
            return {"message": "Admin created"}


@app.get("/")
def read_root():
    return {"message": "Welcome to Eye Injection Appointment System API"}

@app.options("/api/health")
@app.get("/api/health")
def health_check():
    """健康检查端点，用于前端检测后端是否就绪"""
    return {"status": "ok", "message": "Backend is ready"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8031)