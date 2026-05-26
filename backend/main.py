from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from database import create_db_and_tables
from routers import patients_router, appointments_router, data_dictionary_router, system_settings, follow_ups, dashboard, auth
from routers import users as users_router
from models.user import User
from models.system_setting import SystemSetting
from security import get_password_hash
from sqlmodel import Session, select
from database import engine
from auto_migrate import check_and_migrate

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


def _sync_patient_doctors():
    """
    启动时同步患者归属医生：
    patient.doctor 为空时，从该患者最早的一条预约记录中取注药医生填入
    """
    try:
        from models.patient import Patient
        from models.appointment import Appointment
        import logging
        logger = logging.getLogger(__name__)
        
        with Session(engine) as session:
            # 找出 doctor 为空的患者
            patients = session.exec(
                select(Patient).where(
                    Patient.is_deleted == False,
                    (Patient.doctor == None) | (Patient.doctor == ''),
                )
            ).all()
            
            logger.info(f"Found {len(patients)} patients with empty doctor field")
            
            updated = 0
            for p in patients:
                # 取该患者最早的有医生的预约
                appt = session.exec(
                    select(Appointment).where(
                        Appointment.patient_id == p.id,
                        Appointment.is_deleted == False,
                        Appointment.doctor != None,
                        Appointment.doctor != '',
                    ).order_by(Appointment.created_at.asc())
                ).first()
                if appt and appt.doctor:
                    p.doctor = appt.doctor
                    session.add(p)
                    updated += 1
            if updated > 0:
                session.commit()
                logger.info(f"Synced doctor for {updated} patients")
    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Warning: could not sync patient doctors: {e}")
        logger.warning(traceback.format_exc())


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
    
    try:
        # Create default admin user if not exists
        logger.info("Checking admin user...")
        with Session(engine) as session:
            user = session.exec(select(User).where(User.username == "admin")).first()
            if not user:
                admin_user = User(username="admin", hashed_password=get_password_hash("admin"))
                session.add(admin_user)
                session.commit()
                logger.info("Default admin user created.")
            else:
                logger.info("Admin user already exists")

            # Initialize default system settings if not exists
            logger.info("Checking system settings...")
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
            logger.info("System settings initialized")
    except Exception as e:
        logger.error(f"Failed to initialize admin/settings: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return

    logger.info("Startup completed successfully")


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

# 挂载前端静态文件
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

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

@app.options("/api/health")
@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Backend is ready"}
