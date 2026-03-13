"""
Web版本的 FastAPI 应用
包含静态文件服务和前端路由
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import create_db_and_tables
from routers import patients_router, appointments_router, data_dictionary_router, system_settings, follow_ups, dashboard, auth
from models.user import User
from security import get_password_hash
from sqlmodel import Session, select
from database import engine
import os

app = FastAPI(title="眼科注射预约系统 Web版", version="2.1.3-web")

# CORS 配置 - Web版本允许本地访问
origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:4173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:4173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Web版本允许所有来源
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(patients_router, prefix="/api")
app.include_router(appointments_router, prefix="/api")
app.include_router(data_dictionary_router, prefix="/api")
app.include_router(system_settings, prefix="/api")
app.include_router(follow_ups, prefix="/api")
app.include_router(dashboard, prefix="/api")
app.include_router(auth, prefix="/api")

# 静态文件服务
static_dir = "frontend"
if os.path.exists(static_dir):
    # 挂载静态文件目录
    app.mount("/assets", StaticFiles(directory=f"{static_dir}/assets"), name="assets")
    
    # 前端路由处理 - 所有非API路由都返回 index.html
    @app.get("/")
    async def read_index():
        return FileResponse(f"{static_dir}/index.html")
    
    @app.get("/{full_path:path}")
    async def catch_all(full_path: str):
        # API 路由不处理
        if full_path.startswith("api/"):
            return {"error": "API endpoint not found"}
        
        # 检查是否是静态资源
        file_path = os.path.join(static_dir, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # 其他所有路由都返回 index.html (SPA 路由)
        return FileResponse(f"{static_dir}/index.html")

else:
    @app.get("/")
    async def read_root():
        return {
            "message": "眼科注射预约系统 Web版 API",
            "version": "2.1.3-web",
            "error": "前端文件目录不存在，请检查 frontend 目录"
        }

def create_default_user():
    """创建默认用户"""
    try:
        with Session(engine) as session:
            # 检查是否已有用户
            statement = select(User)
            existing_user = session.exec(statement).first()
            
            if not existing_user:
                # 创建默认管理员用户
                default_user = User(
                    username="admin",
                    hashed_password=get_password_hash("admin123"),
                    is_active=True
                )
                session.add(default_user)
                session.commit()
                print("✓ 默认用户已创建 (用户名: admin, 密码: admin123)")
            else:
                print("✓ 用户已存在，跳过创建")
    except Exception as e:
        print(f"创建默认用户失败: {e}")

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    print("🚀 眼科注射预约系统 Web版 启动中...")
    
    # 创建数据库表
    create_db_and_tables()
    print("✓ 数据库表已创建")
    
    # 创建默认用户
    create_default_user()
    
    print("✅ 系统启动完成")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    print("👋 眼科注射预约系统 Web版 已关闭")

# 健康检查接口
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.1.3-web",
        "type": "web"
    }