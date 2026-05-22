import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

print("=== 医生列表 ===")
cursor.execute("SELECT id, category, value, label, is_active FROM data_dictionary WHERE category = 'doctor'")
for row in cursor.fetchall():
    print(row)

print("\n=== 用户列表 ===")
cursor.execute("SELECT id, username, role, doctor, wards FROM user")
for row in cursor.fetchall():
    print(row)

conn.close()
