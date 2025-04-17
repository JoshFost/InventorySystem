from flask import Flask, redirect, url_for, render_template, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from login import User 
import sqlite3
from inventory import init_items_db, add_item, view_items, edit_item, delete_item
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def init_users_db():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Check if an admin user exists; if not, create one
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, role, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                       ('admin', 'password', 'admin', datetime.now(), datetime.now()))
        conn.commit()
        print("Default admin user created: username=admin, password=password")
    conn.close()

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password, role, created_at, updated_at FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    print(f"Loading user: {row}")
    if row:
        return User(*row)
    return None

#login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password, role, created_at, updated_at FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()

        if row and row[2] == password:
            user = User(*row)
            # Check if "Remember me" is selected
            remember = 'remember_me' in request.form
            login_user(user, remember=remember)
            return redirect(url_for('dashboard'))

        flash("Invalid credentials")
    
    return render_template('login.html')

#register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = 'user'
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for('register'))
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()

        if row:
            flash("Username already exists. Please choose another.")
        else:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                           (username, password, role))
            conn.commit()
            flash("Registration successful. Please log in.")
            return redirect(url_for('login')) 

        conn.close()

    return render_template('register.html') 
#protected route
@app.route('/protected')
@login_required
def protected():
    return f"Hello, {current_user.username}! You're logged in."

#log out
@app.route('/logout')
@login_required
def logout():
    logout_user()
   # flash("You have been logged out.", "success")
    return redirect(url_for('login'))

# Default route
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

#items routes
#view items
@app.route('/items', methods=['GET'])
@login_required
def items():
    items = view_items()
    return render_template('items.html', items=items)

#add item
@app.route('/add_item', methods=['GET', 'POST'])
@login_required
def add_item_route(): 
    if current_user.role != 'admin':
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('items'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        try:
            quantity = int(request.form['quantity'])
            price = float(request.form['price'])
            if quantity < 0 or price < 0:
                flash("Quantity and price must be not be negative.", "danger")
                return redirect(url_for('add_item_route'))  
        except ValueError:
            flash("Quantity must be an integer and price must be a number.", "danger")
            return redirect(url_for('add_item_route'))  
        
        add_item(name, description, quantity, price)  
        flash("Item added successfully.", "success")
        return redirect(url_for('items'))
    return render_template('add_item.html') 

#edit item
@app.route('/edit_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item_route(item_id):
    if current_user.role != 'admin':
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('items'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        try:
            quantity = int(request.form['quantity'])
            price = float(request.form['price'])
            if quantity < 0 or price < 0:
                flash("Quantity and price must not be negative.")
                return redirect(url_for('edit_item_route', item_id=item_id))
        except ValueError:
            flash("Quantity and price must be a number.", "danger")
            return redirect(url_for('edit_item_route', item_id=item_id))
        
        edit_item(item_id, name, description, quantity, price)
        flash("Item updated successfully.", "success")
        return redirect(url_for('items')) 
    
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE id=?", (item_id,))
    item = cursor.fetchone()
    conn.close()
    return render_template('edit_item.html', item=item)

#delete item
@app.route('/delete_item/<int:item_id>', methods=['POST'])
@login_required
def delete_item_route(item_id):
    if current_user.role != 'admin':
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('items'))
    #User should not be able to see edit and delete buttons
    delete_item(item_id)
    flash("Item deleted successfully.", "success")
    return redirect(url_for('items'))

#dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM items")
    total_products = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(quantity) FROM items")
    total_items = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(quantity * price) FROM items")
    inventory_value = cursor.fetchone()[0] or 0.0  # Ensure float for currency

    cursor.execute("SELECT COUNT(*) FROM items WHERE quantity < 10")
    low_stock_items = cursor.fetchone()[0]

    conn.close()

    return render_template('dashboard.html',
                           total_products=total_products,
                           total_items=total_items,
                           inventory_value=inventory_value,
                           low_stock_items=low_stock_items)
if __name__ == '__main__':
    init_users_db()  
    init_items_db()  
    app.run(debug=True)
