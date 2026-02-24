from sqlmodel import Session, select, text
from database import engine, create_db_and_tables
from models.user import User
from security import get_password_hash

def check_admin():
    # 1. Drop existing User table to ensure schema update
    with Session(engine) as session:
        try:
            session.exec(text("DROP TABLE user"))
            session.commit()
            print("Dropped existing User table.")
        except Exception as e:
            print(f"Error dropping table (might not exist): {e}")

    # 2. Recreate tables
    create_db_and_tables()
    
    # 3. Create Admin
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == "admin")).first()
        if user:
            print(f"Admin user exists. ID: {user.id}")
            # Reset password just in case
            user.hashed_password = get_password_hash("admin")
            session.add(user)
            session.commit()
            print("Admin password reset to 'admin'")
        else:
            print("Admin user NOT found. Creating...")
            admin_user = User(username="admin", hashed_password=get_password_hash("admin"))
            session.add(admin_user)
            session.commit()
            print("Admin user created with password 'admin'")

if __name__ == "__main__":
    check_admin()
