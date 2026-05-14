import os
import sqlite3
from functools import wraps
from flask import Flask, request, redirect, url_for, session, g, abort, escape
from werkzeug.security import generate_password_hash, check_password_hash

# /home/lucasrobli/experimento-9exe/experimentos/experimento-02/modelo-gpt5.1mini/codigo-gerado.py


# Config
DATABASE = os.path.join(os.path.dirname(__file__), "users.db")
SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(24)

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Database helpers
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
        """
    )
    db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

# Simple login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.before_first_request
def setup():
    init_db()

@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("home"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        if not username or not password:
            return "Usuário e senha são obrigatórios", 400

        db = get_db()
        try:
            pw_hash = generate_password_hash(password)  # pbkdf2:sha256 por padrão
            db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, pw_hash))
            db.commit()
        except sqlite3.IntegrityError:
            return "Nome de usuário já existe", 400
        return redirect(url_for("login"))
    # simple HTML form
    return """
    <h2>Registrar</h2>
    <form method="post">
      <label>Usuário: <input name="username"></label><br>
      <label>Senha: <input type="password" name="password"></label><br>
      <button type="submit">Registrar</button>
    </form>
    <a href="/login">Entrar</a>
    """

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        if not username or not password:
            return "Usuário e senha são obrigatórios", 400

        db = get_db()
        cur = db.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            next_url = request.args.get("next") or url_for("home")
            return redirect(next_url)
        return "Credenciais inválidas", 401

    return """
    <h2>Login</h2>
    <form method="post">
      <label>Usuário: <input name="username"></label><br>
      <label>Senha: <input type="password" name="password"></label><br>
      <button type="submit">Entrar</button>
    </form>
    <a href="/register">Registrar</a>
    """

@app.route("/home")
@login_required
def home():
    username = escape(session.get("username") or "usuário")
    return f"""
    <h2>Bem-vindo, {username}!</h2>
    <p>Rota protegida: /home</p>
    <a href="/dashboard">Ir ao dashboard</a><br>
    <a href="/logout">Sair</a>
    """

@app.route("/dashboard")
@login_required
def dashboard():
    return """
    <h3>Dashboard protegido</h3>
    <p>Apenas usuários autenticados podem ver isto.</p>
    <a href="/home">Voltar</a>
    """

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    # Executar: python codigo-gerado.py
    app.run(host="0.0.0.0", port=5000, debug=True)