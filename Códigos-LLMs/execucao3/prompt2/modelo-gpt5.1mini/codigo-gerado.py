import os
import sqlite3
from flask import Flask, request, redirect, url_for, session, g, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Config
DATABASE = os.path.join(os.path.dirname(__file__), "users.db")
SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(24)

app = Flask(__name__)
app.config.update(SECRET_KEY=SECRET_KEY, DATABASE=DATABASE)


# Database helpers
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


def get_user_by_username(username):
    db = get_db()
    cur = db.execute("SELECT * FROM users WHERE username = ?", (username,))
    return cur.fetchone()


def create_user(username, password):
    db = get_db()
    pw_hash = generate_password_hash(password)
    cur = db.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, pw_hash)
    )
    db.commit()
    return cur.lastrowid


# Authentication helpers
def login_user(user_row):
    session.clear()
    session["user_id"] = user_row["id"]
    session["username"] = user_row["username"]


def logout_user():
    session.clear()


def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    db = get_db()
    cur = db.execute("SELECT id, username FROM users WHERE id = ?", (uid,))
    return cur.fetchone()


def login_required(f):

    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)

    return wrapped


# Routes
@app.before_first_request
def setup():
    init_db()


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        if not username or not password:
            return "Usuário e senha são obrigatórios", 400
        if get_user_by_username(username):
            return "Nome de usuário já existe", 400
        create_user(username, password)
        return redirect(url_for("login"))
    return render_template_string(
        """
        <h2>Registrar</h2>
        <form method="post">
          <label>Usuário: <input name="username"></label><br>
          <label>Senha: <input name="password" type="password"></label><br>
          <button type="submit">Registrar</button>
        </form>
        <a href="{{ url_for('login') }}">Login</a>
        """
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        user = get_user_by_username(username)
        if not user or not check_password_hash(user["password_hash"], password):
            return "Credenciais inválidas", 401
        login_user(user)
        next_url = request.args.get("next") or url_for("home")
        return redirect(next_url)
    return render_template_string(
        """
        <h2>Login</h2>
        <form method="post">
          <label>Usuário: <input name="username"></label><br>
          <label>Senha: <input name="password" type="password"></label><br>
          <button type="submit">Entrar</button>
        </form>
        <a href="{{ url_for('register') }}">Registrar</a>
        """
    )


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/home")
@login_required
def home():
    user = current_user()
    return render_template_string(
        """
        <h2>Bem-vindo, {{ username }}!</h2>
        <p>Esta é a rota /home protegida.</p>
        <a href="{{ url_for('logout') }}">Sair</a>
        """,
        username=user["username"],
    )


@app.route("/protected")
@login_required
def protected():
    user = current_user()
    return f"Rota protegida acessada por {user['username']}"


if __name__ == "__main__":
    app.run(debug=True)