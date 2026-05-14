from flask import Flask, request, redirect, url_for, session, flash, Response
from werkzeug.security import generate_password_hash, check_password_hash
import os
from functools import wraps

# /home/lucasrobli/experimento-10exe/experimentos/experimento-01/modelo-gpt5.1mini/codigo-gerado.py
# Implementação simples de autenticação em Flask.
# O usuário deve realizar login antes de acessar qualquer outra rota.


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "troque-esta-chave-para-producao")

# "Banco de dados" simples em memória. Em produção, substitua por um DB persistente.
users = {
    # usuário de exemplo: admin / senha: secret123
    "admin": {
        "password_hash": generate_password_hash("secret123")
    }
}


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated


@app.before_request
def require_login_for_all_routes():
    # Permitir acesso sem login apenas às rotas listadas:
    allowed_endpoints = {"login", "static", "favicon"}
    if request.endpoint and request.endpoint.split(".")[0] in allowed_endpoints:
        return
    # Se não autenticado, redirecionar para login
    if "user" not in session:
        return redirect(url_for("login", next=request.path))


@app.route("/login", methods=["GET", "POST"])
def login():
    # Formulário de login simples
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = users.get(username)
        if user and check_password_hash(user["password_hash"], password):
            session["user"] = username
            next_url = request.args.get("next") or url_for("index")
            return redirect(next_url)
        flash("Usuário ou senha inválidos.")
        return redirect(url_for("login"))
    # GET -> mostrar formulário
    return Response("""
    <html>
      <head><title>Login</title></head>
      <body>
        <h2>Login</h2>
        <form method="post">
          <label>Usuário: <input name="username" /></label><br/>
          <label>Senha: <input name="password" type="password" /></label><br/>
          <button type="submit">Entrar</button>
        </form>
        <p>Usuário de teste: <b>admin</b> / Senha: <b>secret123</b></p>
      </body>
    </html>
    """, mimetype="text/html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    return f"Olá, {session['user']}! Esta é a página inicial (rota protegida). <a href='{url_for('logout')}'>Sair</a>"


@app.route("/protegido")
@login_required
def protegido():
    return f"Rota protegida acessada por {session['user']}."


# Exemplo de rota pública (se desejar permitir algumas rotas sem login, adicione ao allowed_endpoints)
@app.route("/favicon.ico")
def favicon():
    return "", 204


if __name__ == "__main__":
    # Em produção, utilize um servidor WSGI (gunicorn/uwsgi) e configure DEBUG=False
    app.run(host="0.0.0.0", port=5000, debug=True)