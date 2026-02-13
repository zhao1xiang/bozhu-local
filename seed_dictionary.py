import sqlite3
import uuid
from datetime import datetime

def seed_dictionary():
    conn = sqlite3.connect('backend/database.db')
    cursor = conn.cursor()

    categories = {
        'drug': [
            ('法瑞西单抗', '法瑞西单抗'),
            ('阿柏西普', '阿柏西普'),
            ('雷珠单抗', '雷珠单抗'),
            ('康柏西普', '康柏西普')
        ],
        'diagnosis': [
            ('nAMD', 'nAMD'),
            ('DME', 'DME'),
            ('RVO', 'RVO'),
            ('PCV', 'PCV'),
            ('mCNV', 'mCNV')
        ]
    }

    now = datetime.now().isoformat()

    print("Seeding dictionary data...")
    for category, items in categories.items():
        for i, (label, value) in enumerate(items):
            # Check if exists
            cursor.execute("SELECT id FROM data_dictionary WHERE category = ? AND value = ?", (category, value))
            if not cursor.fetchone():
                item_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO data_dictionary (id, category, label, value, sort_order, is_active, created_at)
                    VALUES (?, ?, ?, ?, ?, 1, ?)
                """, (item_id, category, label, value, i, now))
                print(f"Added {category}: {label}")

    conn.commit()
    conn.close()
    print("Seeding completed.")

if __name__ == "__main__":
    seed_dictionary()
