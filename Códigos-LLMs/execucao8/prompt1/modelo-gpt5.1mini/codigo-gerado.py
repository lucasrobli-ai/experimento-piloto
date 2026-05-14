from flask import Flask, request, redirect, url_for, session, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse, urljoin

app = Flask(__name__)
app.secret_key = "troque-por-uma-chave-secreta-forte"

# Usuários em memória (exemplo). Substitua por DB em produção.
users = {
    "admin": generate_password_hash("senha123")
}

login_form = """
<!doctype html>
<title>Login</title>
<h2>Login</h2>
{% if error %}<p style="color:red;">{{ error }}</p>{% endif %}
<form method="post">
  <label>Usuário: <input type="text" name="username"></label><br>
  <label>Senha: <input type="password" name="password"></label><br>
  <input type="submit" value="Entrar">
</form>
"""

def is_safe_redirect(target):
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return redirect_url.scheme in ('http', 'https') and host_url.netloc == redirect_url.netloc

@app.before_request
def require_login():
    # Rotas que não exigem autenticação
    if request.endpoint in ('login', 'static'):
        return
    if 'user' not in session:
        next_url = request.path
        return redirect(url_for('login', next=next_url))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        pw_hash = users.get(u)
        if pw_hash and check_password_hash(pw_hash, p):
            session['user'] = u
            nxt = request.args.get('next')
            if nxt and is_safe_redirect(nxt):
                return redirect(nxt)
            return redirect(url_for("index"))
        error = "Usuário ou senha incorretos."
    return render_template_string(login_form, error=error)

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route("/")
def index():
    return f"Olá, {session.get('user')}! <a href='{url_for('logout')}'>Sair</a>"

@app.route("/protegido")
def protegido():
    return f"Área protegida para {session.get('user')}."

if __name__ == "__main__":
    app.run(debug=True)