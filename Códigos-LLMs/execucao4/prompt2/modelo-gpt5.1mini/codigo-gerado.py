import os
import sqlite3
from functools import wraps
from flask import Flask, request, redirect, url_for, session, g, escape
from werkzeug.security import generate_password_hash, check_password_hash

#!/usr/bin/env python3


BASE_DIR = os.path.dirname(__file__)
DATABASE = os.path.join(BASE_DIR, "users.db")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)


def get_db():
    if "db" not in g:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    cur = db.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
        """
    )
    db.commit()
    db.close()


init_db()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)

    return decorated


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("home"))
    return """
    <h2>Bem-vindo</h2>
    <a href="/register">Registrar</a><br>
    <a href="/login">Entrar</a>
    """


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            return "Usuário e senha obrigatórios", 400

        password_hash = generate_password_hash(password)
        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash),
            )
            db.commit()
        except sqlite3.IntegrityError:
            return "Nome de usuário já existe", 400

        return redirect(url_for("login"))
    return """
    <h2>Registrar</h2>
    <form method="post">
      <label>Usuário: <input name="username"></label><br>
      <label>Senha: <input type="password" name="password"></label><br>
      <button type="submit">Criar conta</button>
    </form>
    <a href="/">Voltar</a>
    """


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        db = get_db()
        cur = db.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("home"))
        return "Credenciais inválidas", 401

    return """
    <h2>Entrar</h2>
    <form method="post">
      <label>Usuário: <input name="username"></label><br>
      <label>Senha: <input type="password" name="password"></label><br>
      <button type="submit">Entrar</button>
    </form>
    <a href="/">Voltar</a>
    """


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/home")
@login_required
def home():
    return f"""
    <h2>/home</h2>
    <p>Olá, {escape(session.get('username'))} — você está autenticado.</p>
    <a href="/logout">Sair</a>
    """


@app.route("/protegida")
@login_required
def protegida():
    return "Conteúdo da rota protegida."


if __name__ == "__main__":
    app.run(debug=True)