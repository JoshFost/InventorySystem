import sqlite3

conn = sqlite3.connect('inventory.db')
cursor = conn.cursor()
cursor.execute("UPDATE users SET role = 'admin' WHERE username = 'admin'")
conn.commit()
conn.close()
print("Updated admin role to 'admin'.")