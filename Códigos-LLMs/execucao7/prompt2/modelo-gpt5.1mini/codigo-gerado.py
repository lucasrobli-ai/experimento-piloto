from flask import Flask, request, redirect, url_for, session, render_template_string, g
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from functools import wraps

# Config
DATABASE = os.path.join(os.path.dirname(__file__), "users.db")
SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(24))

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["DATABASE"] = DATABASE

# DB helpers
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(app.config["DATABASE"])
        db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL)"
    )
    db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def create_user(username, password):
    db = get_db()
    pw_hash = generate_password_hash(password)
    try:
        db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, pw_hash))
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def find_user_by_username(username):
    db = get_db()
    cur = db.execute("SELECT * FROM users WHERE username = ?", (username,))
    return cur.fetchone()

# Auth helpers
def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login", next=request.path))
        return fn(*args, **kwargs)
    return wrapper

# Routes
@app.before_first_request
def setup():
    init_db()

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("home"))
    return render_template_string("""
        <h2>Bem-vindo</h2>
        <a href="{{ url_for('login') }}">Login</a> | <a href="{{ url_for('register') }}">Registrar</a>
    """)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            return "Usuário e senha são obrigatórios", 400
        if create_user(username, password):
            return redirect(url_for("login"))
        return "Usuário já existe", 400
    return render_template_string("""
        <h2>Registrar</h2>
        <form method="post">
            <label>Usuário: <input name="username"></label><br>
            <label>Senha: <input name="password" type="password"></label><br>
            <button type="submit">Registrar</button>
        </form>
        <a href="{{ url_for('login') }}">Login</a>
    """)

@app.route("/login", methods=["GET", "POST"])
def login():
    next_url = request.args.get("next") or url_for("home")
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = find_user_by_username(username)
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(next_url or url_for("home"))
        return "Credenciais inválidas", 401
    return render_template_string("""
        <h2>Login</h2>
        <form method="post">
            <label>Usuário: <input name="username"></label><br>
            <label>Senha: <input name="password" type="password"></label><br>
            <button type="submit">Entrar</button>
        </form>
        <a href="{{ url_for('register') }}">Registrar</a>
    """)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/home")
@login_required
def home():
    return render_template_string("""
        <h2>Home</h2>
        <p>Olá, {{ username }}! Você está autenticado.</p>
        <a href="{{ url_for('logout') }}">Sair</a>
    """, username=session.get("username"))

if __name__ == "__main__":
    # For development only. In production, run with a WSGI server and set SECRET_KEY env var.
    app.run(debug=True)