import sqlite3

conn = sqlite3.connect('inventory.db')
cursor = conn.cursor()
cursor.execute("SELECT id, username, password, role FROM users WHERE username = 'admin'")
row = cursor.fetchone()
print(row)
conn.close()