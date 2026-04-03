import sqlite3
conn = sqlite3.connect('classroom.db')
conn.row_factory = sqlite3.Row
users = conn.execute('SELECT id, username, plain_password FROM users').fetchall()
for u in users:
    print(f"ID: {u['id']}, Name: {u['username']}, Plain: [{u['plain_password']}]")
conn.close()
