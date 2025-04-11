from flask import Flask, redirect, url_for, render_template, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from login import User 
import sqlite3


app = Flask(__name__)
app.secret_key = 'supersecretkey'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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
            login_user(user)
            return redirect(url_for('protected'))

        flash("Invalid credentials")
    
    return '''
        <form method="post">
            <input type="text" name="username" placeholder="Username"/>
            <input type="password" name="password" placeholder="Password"/>
            <input type="submit" value="Login"/>
        </form>
    '''

#register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = 'user' #default role is user
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for('register'))
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()

        #check if user already exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()

        if row:
            flash("Username already exists. Please choose another.")
        else:
            # Adds new user to user table
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                           (username, password, role))
            conn.commit()
            flash("Registration successful. Please log in.")
            return redirect(url_for('login')) 

        conn.close()

    return '''
        <form method="post">
            <input type="text" name="username" placeholder="Username" required/><br/>
            <input type="password" name="password" placeholder="Password" required/><br/>
            <input type="password" name="confirm_password" placeholder="Confirm Password" required/><br/>
            <input type="submit" value="Register"/>
        </form>
    '''
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
    return redirect(url_for('login'))

#default route
@app.route('/')
def home():
    return "Hello, Flask! Your app is working."

if __name__ == '__main__':
    app.run(debug=True)
