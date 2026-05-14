from flask import Flask, request, redirect, session, url_for, render_template_string, abort
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "troque-esta-chave-para-uma-segura"  # alterar em produção

# Usuários em memória (exemplo). Em produção, usar banco de dados.
users = {
    "alice": generate_password_hash("senha123"),
    "bob": generate_password_hash("senha456"),
}

# Rotas que NÃO exigem autenticação
EXEMPT_ENDPOINTS = {"login", "static"}


@app.before_request
def exigir_login():
    if request.endpoint is None:
        return
    if request.endpoint in EXEMPT_ENDPOINTS:
        return
    if "user" not in session:
        return redirect(url_for("login", next=request.path))


@app.route("/login", methods=["GET", "POST"])
def login():
    next_url = request.args.get("next", "/")
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        pw_hash = users.get(username)
        if pw_hash and check_password_hash(pw_hash, password):
            session["user"] = username
            # evitar redirecionamento para domínios externos
            if not next_url.startswith("/"):
                next_url = "/"
            return redirect(next_url)
        error = "Usuário ou senha inválidos"
        return render_template_string(LOGIN_HTML, error=error, next=next_url)
    return render_template_string(LOGIN_HTML, error=None, next=next_url)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/")
def index():
    return render_template_string(INDEX_HTML, user=session.get("user"))


@app.route("/perfil")
def perfil():
    return render_template_string(PERFIL_HTML, user=session.get("user"))


# HTML simples embutido (para não depender de templates externos)
LOGIN_HTML = """
<!doctype html>
<title>Login</title>
<h2>Login</h2>
{% if error %}<p style="color:red">{{ error }}</p>{% endif %}
<form method="post" action="{{ url_for('login') }}?next={{ next }}">
  <label>Usuário: <input name="username"></label><br>
  <label>Senha: <input name="password" type="password"></label><br>
  <button type="submit">Entrar</button>
</form>
"""

INDEX_HTML = """
<!doctype html>
<title>Início</title>
<h2>Bem-vindo, {{ user }}!</h2>
<p><a href="{{ url_for('perfil') }}">Ver perfil</a></p>
<p><a href="{{ url_for('logout') }}">Sair</a></p>
"""

PERFIL_HTML = """
<!doctype html>
<title>Perfil</title>
<h2>Perfil de {{ user }}</h2>
<p>Informações do usuário (exemplo).</p>
<p><a href="{{ url_for('index') }}">Voltar</a></p>
<p><a href="{{ url_for('logout') }}">Sair</a></p>
"""

if __name__ == "__main__":
    app.run(debug=True)