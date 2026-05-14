from flask import Flask, session, redirect, url_for, request, render_template_string, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "troque-esta-chave-para-produção"

# Usuários em memória (substituir por banco de dados em produção)
users = {
    "admin": generate_password_hash("senha123")
}

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped_view

# Formulário simples de login
login_template = """
<!doctype html>
<title>Login</title>
<h2>Login</h2>
{% with messages = get_flashed_messages() %}
  {% if messages %}
    <ul style="color:red">{% for m in messages %}<li>{{ m }}</li>{% endfor %}</ul>
  {% endif %}
{% endwith %}
<form method="post">
  <label>Usuário: <input name="username"></label><br>
  <label>Senha: <input name="password" type="password"></label><br>
  <button type="submit">Entrar</button>
</form>
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        pwd_hash = users.get(username)
        if pwd_hash and check_password_hash(pwd_hash, password):
            session["user"] = username
            next_page = request.args.get("next") or url_for("index")
            return redirect(next_page)
        flash("Usuário ou senha inválidos.")
    return render_template_string(login_template)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    return f"Olá, {session.get('user')}! Você está autenticado. <a href='{url_for('logout')}'>Sair</a>"

@app.route("/perfil")
@login_required
def perfil():
    return f"Página de perfil de {session.get('user')}."

if __name__ == "__main__":
    app.run(debug=True)