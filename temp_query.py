import sqlite3
conn = sqlite3.connect('simple-web-package-win7-v2.2.3/database.db')
c = conn.cursor()

c.execute("SELECT COUNT(DISTINCT patient_id) FROM appointment WHERE is_deleted=0")
denom = c.fetchone()[0]
print(f'分母（有过预约的患者数）: {denom}')

c.execute("SELECT COUNT(*) FROM appointment WHERE is_deleted=0 AND treatment_phase='强化期' AND doctor='张明明'")
qh = c.fetchone()[0]
print(f'张明明 强化期条数: {qh}')
print(f'强化期约针率: {round(qh/denom*100,1) if denom else 0}%')

c.execute("SELECT appointment_date, treatment_phase, status, patient_id FROM appointment WHERE doctor='张明明' AND is_deleted=0 AND treatment_phase='强化期' LIMIT 20")
rows = c.fetchall()
print(f'张明明强化期预约明细（前20条）:')
for r in rows:
    print(r)
conn.close()
