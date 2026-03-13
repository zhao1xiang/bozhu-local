from sqlmodel import SQLModel, create_engine
from models import Patient, Appointment, PrintRecord, User, SystemSetting, FollowUpRecord


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
