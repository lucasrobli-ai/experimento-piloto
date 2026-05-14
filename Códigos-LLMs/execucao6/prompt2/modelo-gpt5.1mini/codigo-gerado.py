from flask import Flask, request, redirect, url_for, session, g, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from functools import wraps

#!/usr/bin/env python3
# /home/lucasrobli/experimento-6exe/experimentos/experimento-02/modelo-gpt5.1mini/codigo-gerado.py


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_ROOT, "users.db")

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or os.urandom(24)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
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
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    template = """
    <h2>Registrar</h2>
    {% if error %}<p style="color:red">{{ error }}</p>{% endif %}
    <form method="post">
      Usuário: <input name="username" required><br>
      Senha: <input name="password" type="password" required><br>
      Confirmar: <input name="password2" type="password" required><br>
      <button type="submit">Registrar</button>
    </form>
    <p>Já tem conta? <a href="{{ url_for('login') }}">Entrar</a></p>
    """
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")
        if not username or not password:
            error = "Usuário e senha são obrigatórios."
        elif password != password2:
            error = "As senhas não coincidem."
        else:
            db = get_db()
            try:
                db.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                error = "Nome de usuário já existe."
    return render_template_string(template, error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    template = """
    <h2>Login</h2>
    {% if error %}<p style="color:red">{{ error }}</p>{% endif %}
    <form method="post">
      Usuário: <input name="username" required><br>
      Senha: <input name="password" type="password" required><br>
      <button type="submit">Entrar</button>
    </form>
    <p>Não tem conta? <a href="{{ url_for('register') }}">Registrar</a></p>
    """
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        db = get_db()
        user = db.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?", (username,)
        ).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            # redirect to next or /home
            next_page = request.args.get("next")
            return redirect(next_page or url_for("home"))
        error = "Usuário ou senha inválidos."
    return render_template_string(template, error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/home")
@login_required
def home():
    db = get_db()
    user = db.execute("SELECT username FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    username = user["username"] if user else "usuário"
    return f"<h1>Bem-vindo, {username}!</h1><p><a href='{url_for('protected')}'>Rota protegida</a> | <a href='{url_for('logout')}'>Sair</a></p>"


@app.route("/protected")
@login_required
def protected():
    return "<h2>Conteúdo protegido</h2><p>Somente usuários autenticados podem ver isto.</p><p><a href='/home'>Voltar</a></p>"


if __name__ == "__main__":
    app.run(debug=True)