import sqlite3

#crud operations for items
def create_item(name, description, quantity, price):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO items (name, description, quantity, price) VALUES (?, ?, ?, ?)",
                   (name, description, quantity, price))
    conn.commit()
    conn.close()
    print(f"Item '{name}' created.")

def view_items():
    conn= sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    conn.close()
    return items

def edit_item(item_id, name, description, quantity, price):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE items SET name=?, description=?, quantity=?, price=? WHERE id=?",
                   (name, description, quantity, price, item_id))
    conn.commit()
    conn.close()
    print(f"Item with ID {item_id} and name {name} updated.")

def delete_item(item_id):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    print(f"Item with ID {item_id} deleted.")

#initialize the items table
def init_items_db():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP    
        )
    ''')
    conn.commit()
    conn.close()
    print("Items table initialised.")
