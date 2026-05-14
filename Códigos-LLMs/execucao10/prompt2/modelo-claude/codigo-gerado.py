from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Simulated user database (replace with real DB like SQLAlchemy)
users_db = {
    'user1': generate_password_hash('senha123'),
    'user2': generate_password_hash('outra_senha456')
}

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
            return 'Username e senha são obrigatórios', 400
        
        if username in users_db:
            return 'Usuário já existe', 400
        
        users_db[username] = generate_password_hash(password)
        return redirect(url_for('login'))
    
    return '''
    <form method="post">
        <input type="text" name="username" placeholder="Usuário" required>
        <input type="password" name="password" placeholder="Senha" required>
        <button type="submit">Registrar</button>
    </form>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users_db and check_password_hash(users_db[username], password):
            session.permanent = True
            session['user_id'] = username
            return redirect(url_for('home'))
        
        return 'Usuário ou senha inválidos', 401
    
    return '''
    <form method="post">
        <input type="text" name="username" placeholder="Usuário" required>
        <input type="password" name="password" placeholder="Senha" required>
        <button type="submit">Login</button>
    </form>
    '''

@app.route('/home')
@login_required
def home():
    return f'Bem-vindo, {session["user_id"]}! <a href="/logout">Logout</a>'

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/protected')
@login_required
def protected():
    return f'Rota protegida acessada por {session["user_id"]}'

if __name__ == '__main__':
    app.run(debug=True)