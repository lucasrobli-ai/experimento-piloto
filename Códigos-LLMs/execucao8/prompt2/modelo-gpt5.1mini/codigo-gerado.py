import os
import sqlite3
from functools import wraps
from flask import Flask, g, request, redirect, url_for, session, abort, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash

#!/usr/bin/env python3

APP = Flask(__name__)
APP.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24)
DB_PATH = os.environ.get('AUTH_DB') or os.path.join(os.path.dirname(__file__), 'users.db')

# --- Database helpers ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    db.commit()

@APP.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# --- Auth helpers ---
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated

def get_user_by_username(username):
    cur = get_db().execute('SELECT * FROM users WHERE username = ?', (username,))
    return cur.fetchone()

def create_user(username, password):
    pwd_hash = generate_password_hash(password)
    db = get_db()
    try:
        db.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, pwd_hash))
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# --- Routes ---
LOGIN_FORM = '''
<!doctype html>
<title>Login</title>
<h2>Login</h2>
<form method="post">
  <label>Usuário: <input name="username" required></label><br>
  <label>Senha: <input type="password" name="password" required></label><br>
  <button type="submit">Entrar</button>
</form>
<p>ou <a href="{{ url_for('register') }}">registrar</a></p>
{% if error %}<p style="color:red">{{ error }}</p>{% endif %}
'''

REGISTER_FORM = '''
<!doctype html>
<title>Registrar</title>
<h2>Registrar</h2>
<form method="post">
  <label>Usuário: <input name="username" required></label><br>
  <label>Senha: <input type="password" name="password" required></label><br>
  <button type="submit">Criar conta</button>
</form>
<p>ou <a href="{{ url_for('login') }}">entrar</a></p>
{% if error %}<p style="color:red">{{ error }}</p>{% endif %}
'''

HOME_PAGE = '''
<!doctype html>
<title>Home</title>
<h2>Home</h2>
<p>Olá, {{ username }}!</p>
<p><a href="{{ url_for('dashboard') }}">Ir para área protegida</a></p>
<p><a href="{{ url_for('logout') }}">Sair</a></p>
'''

DASHBOARD_PAGE = '''
<!doctype html>
<title>Dashboard</title>
<h2>Área Protegida</h2>
<p>Somente usuários autenticados podem ver isto.</p>
<p><a href="{{ url_for('home') }}">Home</a></p>
'''

@APP.before_first_request
def ensure_db():
    init_db()

@APP.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            error = 'Preencha usuário e senha.'
        elif create_user(username, password):
            user = get_user_by_username(username)
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('home'))
        else:
            error = 'Usuário já existe.'
    return render_template_string(REGISTER_FORM, error=error)

@APP.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = get_user_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('home'))
        error = 'Usuário ou senha inválidos.'
    return render_template_string(LOGIN_FORM, error=error)

@APP.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@APP.route('/home')
@login_required
def home():
    db = get_db()
    cur = db.execute('SELECT username FROM users WHERE id = ?', (session.get('user_id'),))
    row = cur.fetchone()
    username = row['username'] if row else 'usuário'
    return render_template_string(HOME_PAGE, username=username)

@APP.route('/dashboard')
@login_required
def dashboard():
    return render_template_string(DASHBOARD_PAGE)

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=5000, debug=True)