from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Simulando um banco de dados de usuários
# Em produção, use um banco de dados real
users_db = {}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return 'Username and password are required', 400
        
        if username in users_db:
            return 'User already exists', 400
        
        hashed_password = generate_password_hash(password)
        users_db[username] = hashed_password
        
        return redirect(url_for('login'))
    
    return '''
    <form method="post">
        <input type="text" name="username" placeholder="Username" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Register</button>
    </form>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users_db and check_password_hash(users_db[username], password):
            session['user_id'] = username
            return redirect(url_for('home'))
        
        return 'Invalid username or password', 401
    
    return '''
    <form method="post">
        <input type="text" name="username" placeholder="Username" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Login</button>
    </form>
    <p><a href="/register">Register here</a></p>
    '''

@app.route('/home')
@login_required
def home():
    username = session.get('user_id')
    return f'<h1>Welcome, {username}!</h1><a href="/logout">Logout</a>'

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/protected')
@login_required
def protected():
    return 'This is a protected route'

if __name__ == '__main__':
    app.run(debug=False)