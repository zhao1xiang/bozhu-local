from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_db_and_tables
from routers import patients_router, appointments_router, data_dictionary_router, system_settings, follow_ups, dashboard, auth
from models.user import User
from security import get_password_hash
from sqlmodel import Session, select
from database import engine

app = FastAPI()

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
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # Create default admin user if not exists
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == "admin")).first()
        if not user:
            # Create admin user
            admin_user = User(username="admin", hashed_password=get_password_hash("admin"))
            session.add(admin_user)
            session.commit()
            print("Default admin user created.")

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
