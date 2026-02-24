import sqlite3

def migrate():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    print("Checking patient table...")
    cursor.execute("PRAGMA table_info(patient)")
    patient_cols = [col[1] for col in cursor.fetchall()]
    if 'patient_type' not in patient_cols:
        print("Adding patient_type to patient table...")
        cursor.execute("ALTER TABLE patient ADD COLUMN patient_type TEXT")
    
    print("Checking appointment table...")
    cursor.execute("PRAGMA table_info(appointment)")
    appointment_cols = [col[1] for col in cursor.fetchall()]
    if 'treatment_phase' not in appointment_cols:
        print("Adding treatment_phase to appointment table...")
        cursor.execute("ALTER TABLE appointment ADD COLUMN treatment_phase TEXT")
    
    # Optional: cleanup is_te_scheme if we really want to, but it doesn't hurt.
    # SQLite doesn't support DROP COLUMN in older versions easily (needs table recreation).
    # Since it's harmless, we leave it.
    
    conn.commit()
    conn.close()
    print("Migration completed.")

if __name__ == "__main__":
    migrate()
