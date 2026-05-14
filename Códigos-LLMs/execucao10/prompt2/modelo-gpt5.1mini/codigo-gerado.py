from flask import Flask, request, redirect, session, g, render_template_string, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from functools import wraps

DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(24)


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop('db', None)
    if db is not None:
        db.close()


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


@app.before_first_request
def initialize():
    init_db()


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.path))
        return fn(*args, **kwargs)
    return wrapper


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template_string('''
        <h2>Bem-vindo</h2>
        <a href="{{ url_for('login') }}">Login</a> |
        <a href="{{ url_for('register') }}">Registrar</a>
    ''')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            return "Usuário e senha obrigatórios", 400
        db = get_db()
        try:
            db.execute(
                'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
        except sqlite3.IntegrityError:
            return "Nome de usuário já existe", 400
        return redirect(url_for('login'))
    return render_template_string('''
        <h2>Registrar</h2>
        <form method="post">
            <label>Usuário: <input name="username"></label><br>
            <label>Senha: <input name="password" type="password"></label><br>
            <button type="submit">Criar conta</button>
        </form>
        <a href="{{ url_for('index') }}">Voltar</a>
    ''')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        db = get_db()
        row = db.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,)).fetchone()
        if row and check_password_hash(row['password_hash'], password):
            session.clear()
            session['user_id'] = row['id']
            session['username'] = username
            next_url = request.args.get('next') or url_for('home')
            return redirect(next_url)
        return "Credenciais inválidas", 401
    return render_template_string('''
        <h2>Login</h2>
        <form method="post">
            <label>Usuário: <input name="username"></label><br>
            <label>Senha: <input name="password" type="password"></label><br>
            <button type="submit">Entrar</button>
        </form>
        <a href="{{ url_for('register') }}">Registrar</a>
    ''')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/home')
@login_required
def home():
    return render_template_string('''
        <h2>Home</h2>
        <p>Olá, {{ username }}! Você está autenticado.</p>
        <a href="{{ url_for('logout') }}">Sair</a>
    ''', username=session.get('username'))


if __name__ == '__main__':
    app.run(debug=True)