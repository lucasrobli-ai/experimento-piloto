from flask import Flask, request, redirect, url_for, session, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "troque-esta-chave-para-ambiente"  # troque em produção

# Usuários em memória (username: password_hash)
USERS = {
    "admin": generate_password_hash("senha123")
}

login_template = """
<!doctype html>
<title>Login</title>
<h2>Login</h2>
{% if error %}<p style="color:red">{{ error }}</p>{% endif %}
<form method="post">
  <label>Usuário: <input name="username"></label><br>
  <label>Senha: <input name="password" type="password"></label><br>
  <input type="hidden" name="next" value="{{ next }}">
  <button type="submit">Entrar</button>
</form>
"""

home_template = """
<!doctype html>
<title>Home</title>
<h2>Bem-vindo, {{ user }}</h2>
<p><a href="{{ url_for('secret') }}">Ir para rota protegida</a></p>
<p><a href="{{ url_for('logout') }}">Sair</a></p>
"""

secret_template = """
<!doctype html>
<title>Segredo</title>
<h2>Rota protegida</h2>
<p>Somente usuários autenticados podem ver isto.</p>
<p><a href="{{ url_for('index') }}">Voltar</a></p>
"""

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    next_url = request.values.get("next") or url_for("index")
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        pw_hash = USERS.get(username)
        if pw_hash and check_password_hash(pw_hash, password):
            session["user"] = username
            return redirect(next_url)
        error = "Usuário ou senha inválidos"
    return render_template_string(login_template, error=error, next=next_url)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    return render_template_string(home_template, user=session.get("user"))

@app.route("/secret")
@login_required
def secret():
    return render_template_string(secret_template)

if __name__ == "__main__":
    app.run(debug=True)