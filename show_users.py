import sqlite3
conn = sqlite3.connect('instance/talent_portal.db')
cur = conn.cursor()
cur.execute('SELECT id, email, role, password_hash FROM users')
rows = cur.fetchall()
print(f"{'ID':<4} {'Email':<30} {'Role':<10} {'Password Hash'}")
print('-' * 110)
for r in rows:
    print(f"{r[0]:<4} {r[1]:<30} {r[2]:<10} {r[3]}")
conn.close()
