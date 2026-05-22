from sqlmodel import SQLModel, create_engine
from models import Patient, Appointment, PrintRecord, User, SystemSetting, FollowUpRecord
import os

# 使用当前工作目录下的 database.db（支持任意目录运行）
sqlite_file_name = os.path.join(os.getcwd(), "database.db")
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
