import sqlite3
import os

def migrate():
    db_path = 'database.db'
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        columns_to_add = [
            ("pre_op_vision", "FLOAT"),
            ("pre_op_cst", "FLOAT")
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                print(f"Attempting to add column {col_name}...")
                cursor.execute(f"ALTER TABLE appointment ADD COLUMN {col_name} {col_type}")
                print(f"Successfully added column {col_name}")
            except sqlite3.OperationalError as e:
                # Column likely already exists
                print(f"Could not add column {col_name}: {e}")
            
        conn.commit()
        conn.close()
        print("Migration process completed.")
    except Exception as e:
        print(f"Migration failed completely: {e}")

if __name__ == "__main__":
    migrate()
