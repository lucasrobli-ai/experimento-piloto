import os
import sqlite3
from functools import wraps
from flask import Flask, request, redirect, url_for, session, g, abort, escape
from werkzeug.security import generate_password_hash, check_password_hash

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /home/lucasrobli/experimento-5exe/experimentos/experimento-02/modelo-gpt5.1mini/codigo-gerado.py



DATABASE = os.path.join(os.path.dirname(__file__), 'users.db')
SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)

app = Flask(__name__)
app.secret_key = SECRET_KEY


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
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
        );
    ''')
    db.commit()


@app.before_first_request
def prepare():
    init_db()


def create_user(username, password):
    db = get_db()
    pw_hash = generate_password_hash(password)
    try:
        db.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                   (username, pw_hash))
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def get_user_by_username(username):
    db = get_db()
    cur = db.execute('SELECT * FROM users WHERE username = ?', (username,))
    return cur.fetchone()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return '''
    <h2>Bem-vindo</h2>
    <a href="/login">Login</a> | <a href="/register">Registrar</a>
    '''


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            return 'Nome de usuário e senha são obrigatórios.', 400
        if create_user(username, password):
            return redirect(url_for('login'))
        return 'Nome de usuário já existe.', 400
    return '''
    <h2>Registrar</h2>
    <form method="post">
      <label>Usuário: <input name="username"></label><br>
      <label>Senha: <input type="password" name="password"></label><br>
      <button type="submit">Registrar</button>
    </form>
    <a href="/login">Login</a>
    '''


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = get_user_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['id']
            # redirect to next or /home
            nxt = request.args.get('next') or url_for('home')
            return redirect(nxt)
        return 'Credenciais inválidas.', 401
    return '''
    <h2>Login</h2>
    <form method="post">
      <label>Usuário: <input name="username"></label><br>
      <label>Senha: <input type="password" name="password"></label><br>
      <button type="submit">Entrar</button>
    </form>
    <a href="/register">Registrar</a>
    '''


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/home')
@login_required
def home():
    # show current username
    db = get_db()
    cur = db.execute('SELECT username FROM users WHERE id = ?', (session['user_id'],))
    row = cur.fetchone()
    username = escape(row['username']) if row else 'usuário'
    return f'''
    <h2>Home</h2>
    <p>Olá, {username}!</p>
    <a href="/logout">Sair</a>
    '''


if __name__ == '__main__':
    # para desenvolvimento apenas; em produção use um servidor WSGI
    app.run(host='127.0.0.1', port=5000, debug=True)