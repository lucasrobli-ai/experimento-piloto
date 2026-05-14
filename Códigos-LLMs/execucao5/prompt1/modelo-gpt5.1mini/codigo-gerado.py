from flask import Flask, request, redirect, url_for, session, render_template_string, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os

# codigo-gerado.py

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Usuários em memória (substituir por DB em produção)
users = {
    "admin": generate_password_hash("admin123"),
    "usuario": generate_password_hash("senha")
}

# Rotas de template simples embutidas
LOGIN_HTML = """
<!doctype html>
<title>Login</title>
<h2>Login</h2>
{% with messages = get_flashed_messages() %}
  {% if messages %}<ul>{% for m in messages %}<li>{{ m }}</li>{% endfor %}</ul>{% endif %}
{% endwith %}
<form method=post>
  <label>Usuário: <input name=username></label><br>
  <label>Senha: <input name=password type=password></label><br>
  <input type=hidden name=next value="{{ next }}">
  <button type=submit>Entrar</button>
</form>
"""

DASHBOARD_HTML = """
<!doctype html>
<title>Dashboard</title>
<h2>Bem-vindo, {{ user }}!</h2>
<p>Esta é uma rota protegida.</p>
<p><a href="{{ url_for('logout') }}">Sair</a></p>
"""

# Antes de cada requisição, exige login para todas as rotas exceto /login e assets estáticos
@app.before_request
def require_login():
    allowed_endpoints = ('login', 'static',)
    if request.endpoint in allowed_endpoints:
        return
    if 'user' not in session:
        return redirect(url_for('login', next=request.path))

@app.route('/login', methods=['GET', 'POST'])
def login():
    next_page = request.values.get('next') or url_for('dashboard')
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        pw_hash = users.get(username)
        if pw_hash and check_password_hash(pw_hash, password):
            session.clear()
            session['user'] = username
            return redirect(next_page)
        flash('Usuário ou senha inválidos')
    return render_template_string(LOGIN_HTML, next=next_page)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    return render_template_string(DASHBOARD_HTML, user=session.get('user'))

if __name__ == '__main__':
    app.run(debug=True)