from flask import Flask, g, request, redirect, url_for, session, render_template_string
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

# /home/lucasrobli/experimento-2exe/experimentos/experimento-01/modelo-gpt5.1mini/codigo-gerado.py

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")
SECRET_KEY = "dev-secret-key"  # trocar em produção

app = Flask(__name__)
app.secret_key = SECRET_KEY

# --- DB helpers ---
def get_db():
    db = getattr(g, "_db", None)
    if db is None:
        db = g._db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    db = sqlite3.connect(DB_PATH)
    c = db.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    # cria usuário padrão se não existir
    c.execute("SELECT id FROM users WHERE username = ?", ("admin",))
    if c.fetchone() is None:
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                  ("admin", generate_password_hash("secret")))
    db.commit()
    db.close()

@app.teardown_appcontext
def close_db(exc):
    db = getattr(g, "_db", None)
    if db is not None:
        db.close()

# --- Autenticação ---
def get_user_by_username(username):
    db = get_db()
    cur = db.execute("SELECT * FROM users WHERE username = ?", (username,))
    return cur.fetchone()

# Bloqueia acesso a todas as rotas exceto login e static
@app.before_request
def require_login():
    allowed_endpoints = ("login", "static")
    if request.endpoint in allowed_endpoints:
        return
    # permitir acesso a recursos sem endpoint (favicon etc.)
    if request.endpoint is None:
        return
    if "user_id" not in session:
        return redirect(url_for("login", next=request.path))

# --- Rotas ---
LOGIN_HTML = """
<!doctype html>
<title>Login</title>
<h2>Login</h2>
{% if error %}<p style="color:red">{{ error }}</p>{% endif %}
<form method="post">
  <label>Usuário: <input name="username"></label><br>
  <label>Senha: <input name="password" type="password"></label><br>
  <button type="submit">Entrar</button>
</form>
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_user_by_username(username)
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            nxt = request.args.get("next") or url_for("dashboard")
            return redirect(nxt)
        error = "Credenciais inválidas"
    return render_template_string(LOGIN_HTML, error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def index():
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    return f"Olá, {session.get('username')}! Esta é a área protegida."

# Rota para criar novos usuários (exemplo mínimo, proteger em produção)
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            return "username and password required", 400
        db = get_db()
        try:
            db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                       (username, generate_password_hash(password)))
            db.commit()
        except sqlite3.IntegrityError:
            return "username already exists", 400
        return redirect(url_for("login"))
    return """
    <form method="post">
      <input name="username" placeholder="username">
      <input name="password" type="password" placeholder="password">
      <button type="submit">Register</button>
    </form>
    """

if __name__ == "__main__":
    init_db()
    app.run(debug=True)