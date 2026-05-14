from flask import Flask, request, session, redirect, url_for, escape
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse, urljoin

app = Flask(__name__)
app.secret_key = "troque-esta-chave-por-uma-secreta-e-segura"

# Usuários de exemplo (em produção, use banco de dados)
USERS = {
    "admin": generate_password_hash("senha123"),
    "user": generate_password_hash("teste")
}

def is_safe_url(target):
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return redirect_url.scheme in ("http", "https") and host_url.netloc == redirect_url.netloc

@app.before_request
def require_login():
    # Permitir acesso às rotas de login, logout e arquivos estáticos sem autenticação
    allowed_endpoints = {"login", "static"}
    if request.endpoint in allowed_endpoints:
        return
    if "user_id" not in session:
        next_url = request.full_path if request.query_string else request.path
        if not is_safe_url(next_url):
            next_url = "/"
        return redirect(url_for("login", next=next_url))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        pw_hash = USERS.get(username)
        if pw_hash and check_password_hash(pw_hash, password):
            session["user_id"] = username
            next_url = request.args.get("next") or url_for("dashboard")
            if not is_safe_url(next_url):
                next_url = url_for("dashboard")
            return redirect(next_url)
        return """
            <p>Credenciais inválidas.</p>
            <a href="/login">Tentar novamente</a>
        """, 401
    return """
        <h2>Login</h2>
        <form method="post">
            <label>Usuário: <input name="username"></label><br>
            <label>Senha: <input name="password" type="password"></label><br>
            <button type="submit">Entrar</button>
        </form>
    """

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

@app.route("/")
def index():
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    user = escape(session.get("user_id"))
    return f"""
        <h1>Dashboard</h1>
        <p>Usuário autenticado: {user}</p>
        <p><a href="{url_for('logout')}">Sair</a></p>
    """

if __name__ == "__main__":
    app.run(debug=True)