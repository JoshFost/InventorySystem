import sqlite3
from flask_login import UserMixin


def init_login_db():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP    
        )
    ''')
    conn.commit()
    conn.close()


class User(UserMixin):
    def __init__(self, id, username, password, role, created_at, updated_at):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        self.created_at = created_at
        self.updated_at = updated_at


#check the database works as expected
if __name__ == "__main__":
    init_login_db()
    print("User table initialized.")

#test cases
def add_test_user():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("admin", "password"))
    conn.commit()
    conn.close()
    print("Test user added.")

if __name__ == "__main__":
    init_login_db()
    add_test_user()
