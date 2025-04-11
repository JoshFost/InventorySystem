import sqlite3

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