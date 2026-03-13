import sqlite3
import uuid
import random
from datetime import datetime, timedelta

def generate_data():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Clear existing data for clean demo
    print("Cleaning existing data...")
    cursor.execute("DELETE FROM followuprecord")
    cursor.execute("DELETE FROM appointment")
    cursor.execute("DELETE FROM patient")

    diseases = ["nAMD", "DME", "RVO", "PCV", "mCNV"]
    drugs = ["法瑞西单抗", "阿柏西普", "雷珠单抗", "康柏西普"]
    doctors = ["张医生", "王医生", "李医生", "陈医生"]
    cost_types = ["医保", "自费", "公费"]
    phases = ["强化期", "巩固期"]
    patient_types = ["初治", "经治"]

    today = datetime.now()
    start_date = today - timedelta(days=180)

    print("Generating patients and appointments...")
    for i in range(100): # Increase to 100 for better distribution
        p_id = str(uuid.uuid4())
        name = f"患者{i+1:02d}"
        disease = random.choice(diseases)
        drug = random.choice(drugs)
        p_type = random.choice(patient_types)
        
        # Randomize start date: some old, some very recent
        # 70% are recent (within last 40 days) to highlight loading phase
        if random.random() < 0.7:
            p_start_date = today - timedelta(days=random.randint(0, 40))
        else:
            p_start_date = start_date + timedelta(days=random.randint(0, 100))

        # Insert Patient
        cursor.execute("""
            INSERT INTO patient (id, name, diagnosis, drug_type, patient_type, status, created_at, updated_at, left_eye, right_eye)
            VALUES (?, ?, ?, ?, ?, 'active', ?, ?, ?, ?)
        """, (p_id, name, disease, drug, p_type, p_start_date.isoformat(), p_start_date.isoformat(), random.choice([0,1]), random.choice([0,1])))

        # Generate appointments for this patient
        num_appointments = random.randint(3, 8)
        current_date = p_start_date
        
        # High probability (85%) of having the next one scheduled if not all 8 are done
        will_book_next = random.random() < 0.85

        for j in range(num_appointments):
            a_id = str(uuid.uuid4())
            # Logic: First one always happens. 
            # If current_date < today, it's completed.
            # If current_date >= today, it's scheduled.
            status = "completed" if current_date < today else "scheduled"
            
            # If we decided this patient won't book next, stop after some completed ones
            if not will_book_next and current_date >= today:
                break

            phase = "强化期" if j < 3 else "巩固期"
            
            cursor.execute("""
                INSERT INTO appointment (
                    id, patient_id, appointment_date, status, injection_count, 
                    drug_name, doctor, cost_type, treatment_phase, eye,
                    created_at, updated_at, is_te_scheme
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """, (
                a_id, p_id, current_date.date().isoformat(), status, j + 1,
                drug, random.choice(doctors), random.choice(cost_types), phase, 
                random.choice(["左眼", "右眼", "双眼"]),
                p_start_date.isoformat(), datetime.now().isoformat()
            ))
            
            # Increment date
            if phase == "强化期":
                current_date += timedelta(days=random.randint(28, 35))
            else:
                current_date += timedelta(days=random.randint(60, 90))
            
            # Ensure we don't schedule too far into the future beyond what's helpful
            if current_date > today + timedelta(days=120):
                break

    conn.commit()
    conn.close()
    print("Demo data generation completed.")

if __name__ == "__main__":
    generate_data()
