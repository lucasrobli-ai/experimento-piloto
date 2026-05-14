import os
import sqlite3
import functools
from flask import Flask, request, redirect, url_for, session, g, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash

# codigo-gerado.py

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db:
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


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped_view


# Simple templates in-file
LOGIN_HTML = """
<!doctype html>
<title>Login</title>
<h2>Login</h2>
<form method=post>
  <label>Username: <input name=username></label><br>
  <label>Password: <input type=password name=password></label><br>
  <input type=submit value=Login>
</form>
<p>Não tem conta? <a href="{{ url_for('register') }}">Registrar</a></p>
{% if error %}<p style="color:red">{{ error }}</p>{% endif %}
"""

REGISTER_HTML = """
<!doctype html>
<title>Register</title>
<h2>Registrar</h2>
<form method=post>
  <label>Username: <input name=username></label><br>
  <label>Password: <input type=password name=password></label><br>
  <input type=submit value=Registrar>
</form>
<p>Já tem conta? <a href="{{ url_for('login') }}">Login</a></p>
{% if error %}<p style="color:red">{{ error }}</p>{% endif %}
"""

HOME_HTML = """
<!doctype html>
<title>Home</title>
<h2>Bem-vindo, {{ username }}</h2>
<p>Esta é a página /home (protegida).</p>
<p><a href="{{ url_for('protected') }}">Rota Protegida</a> | <a href="{{ url_for('logout') }}">Sair</a></p>
"""

PROTECTED_HTML = """
<!doctype html>
<title>Protegido</title>
<h2>Rota Protegida</h2>
<p>Somente usuários autenticados podem ver isto.</p>
<p><a href="{{ url_for('home') }}">Home</a> | <a href="{{ url_for('logout') }}">Sair</a></p>
"""


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        if not username or not password:
            error = "Username e senha são obrigatórios."
        else:
            db = get_db()
            cur = db.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cur.fetchone():
                error = "Username já existe."
            else:
                pw_hash = generate_password_hash(password)
                db.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, pw_hash),
                )
                db.commit()
                return redirect(url_for("login"))
    return render_template_string(REGISTER_HTML, error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        db = get_db()
        cur = db.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        if user is None or not check_password_hash(user["password_hash"], password):
            error = "Credenciais inválidas."
        else:
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = username
            return redirect(url_for("home"))
    return render_template_string(LOGIN_HTML, error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/home")
@login_required
def home():
    return render_template_string(HOME_HTML, username=session.get("username"))


@app.route("/protected")
@login_required
def protected():
    return render_template_string(PROTECTED_HTML)


if __name__ == "__main__":
    # Executar: python codigo-gerado.py
    app.run(debug=True)