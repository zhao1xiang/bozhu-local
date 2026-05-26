"""
主应用程序 - 包含静态文件服务
用于 PyInstaller 打包的 Web 服务器
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import create_db_and_tables
from routers import patients_router, appointments_router, data_dictionary_router, system_settings, follow_ups, dashboard, auth
from models.user import User
from models.system_setting import SystemSetting
from security import get_password_hash
from sqlmodel import Session, select
from database import engine

app = FastAPI()

# 开发环境允许所有来源，生产环境使用白名单
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:4173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:4173",
    "http://127.0.0.1:38125",
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

@app.on_event("startup")
def on_startup():
    import logging
    logger = logging.getLogger(__name__)
    
    create_db_and_tables()
    
    # 运行数据库迁移
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
    
    # Create default admin user if not exists
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == "admin")).first()
        if not user:
            # Create admin user
            admin_user = User(username="admin", hashed_password=get_password_hash("admin"))
            session.add(admin_user)
            session.commit()
            print("Default admin user created.")
        
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
                print(f"Created default system setting: {key} = {default_value}")
        
        session.commit()

# 包含所有 API 路由 - 必须在 mount 之前
app.include_router(patients_router, prefix="/api")
app.include_router(appointments_router, prefix="/api")
app.include_router(data_dictionary_router, prefix="/api")
app.include_router(system_settings.router, prefix="/api")
app.include_router(follow_ups.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(auth.router, prefix="/api")

from routers.embed import router as embed_router
app.include_router(embed_router, prefix="/api")

@app.options("/api/health")
@app.get("/api/health")
def health_check():
    """健康检查端点，用于前端检测后端是否就绪"""
    return {"status": "ok", "message": "Backend is ready"}

@app.get("/api/debug/files")
def debug_files():
    """调试端点：显示当前目录和前端文件"""
    import os
    current_dir = os.getcwd()
    frontend_dir = "frontend"
    
    result = {
        "current_directory": current_dir,
        "frontend_dir_exists": os.path.exists(frontend_dir),
        "frontend_dir_path": os.path.abspath(frontend_dir),
    }
    
    if os.path.exists(frontend_dir):
        result["frontend_contents"] = os.listdir(frontend_dir)
    
    return result

# 挂载前端静态文件 - 必须在所有 API 路由之后
# 检查前端目录是否存在
frontend_dir = "frontend"
frontend_path = os.path.abspath(frontend_dir)

print(f"[Frontend] 当前工作目录: {os.getcwd()}")
print(f"[Frontend] 查找前端目录: {frontend_dir}")
print(f"[Frontend] 绝对路径: {frontend_path}")

if os.path.exists(frontend_dir):
    print(f"[Frontend] 找到前端目录")
    try:
        contents = os.listdir(frontend_dir)
        print(f"[Frontend] 目录内容: {contents}")
        # 挂载前端资源目录 - 这必须是最后一个 mount，因为它会捕获所有未匹配的路由
        app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
        print(f"[Frontend] 前端静态文件已挂载到 /")
    except Exception as e:
        print(f"[Frontend] 挂载失败: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"[Frontend] 前端目录不存在")
    print(f"[Frontend] 当前目录内容: {os.listdir('.')}")
    print(f"[Frontend] 跳过静态文件挂载")
