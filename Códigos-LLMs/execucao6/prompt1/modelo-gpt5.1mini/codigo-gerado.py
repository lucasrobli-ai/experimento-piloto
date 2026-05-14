from flask import Flask, request, redirect, url_for, session, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash

# /home/lucasrobli/experimento-6exe/experimentos/experimento-01/modelo-gpt5.1mini/codigo-gerado.py

app = Flask(__name__)
app.secret_key = "troque-esta-chave-por-uma-secreta-e-complexa"

# Usuários em memória (exemplo). Em produção, use um banco de dados.
users = {
    "admin": generate_password_hash("senha123"),
    "usuario": generate_password_hash("teste")
}

# Páginas que não exigem autenticação
PUBLIC_PATHS = ["/login", "/static/", "/favicon.ico"]


def is_public_path(path):
    for p in PUBLIC_PATHS:
        if path == p or path.startswith(p):
            return True
    return False


@app.before_request
def exigir_login():
    # Permite chamadas de arquivos estáticos e a rota de login
    if is_public_path(request.path):
        return
    # Permite endpoints usados internamente (OPTIONS, etc.)
    if request.method == "OPTIONS":
        return
    # Se não estiver autenticado, redireciona ao login (mantém next)
    if "user" not in session:
        next_path = request.path
        return redirect(url_for("login", next=next_path))


@app.route("/login", methods=["GET", "POST"])
def login():
    next_path = request.args.get("next") or url_for("dashboard")
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        pw_hash = users.get(username)
        if pw_hash and check_password_hash(pw_hash, password):
            session["user"] = username
            # Só permite redirecionamento interno
            if next_path and next_path.startswith("/"):
                return redirect(next_path)
            return redirect(url_for("dashboard"))
        error = "Usuário ou senha inválidos."
    else:
        error = None

    return render_template_string(
        """
        <!doctype html>
        <title>Login</title>
        <h2>Login</h2>
        {% if error %}<p style="color:red">{{ error }}</p>{% endif %}
        <form method="post">
            <label>Usuário: <input name="username"></label><br>
            <label>Senha: <input name="password" type="password"></label><br>
            <button type="submit">Entrar</button>
        </form>
        """,
        error=error,
    )


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/")
def index():
    # Redireciona para área protegida
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    user = session.get("user")
    return render_template_string(
        """
        <!doctype html>
        <title>Dashboard</title>
        <h2>Bem-vindo, {{ user }}!</h2>
        <p>Esta rota requer autenticação.</p>
        <p><a href="{{ url_for('logout') }}">Sair</a></p>
        """,
        user=user,
    )


if __name__ == "__main__":
    app.run(debug=True)