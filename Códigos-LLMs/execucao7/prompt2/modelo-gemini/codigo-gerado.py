from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import functools

app = Flask(__name__)
app.secret_key = 'uma_chave_muito_secreta_e_aleatoria' # Substitua por uma chave forte em produção

# Simula um banco de dados de usuários
users = {} # { "username": {"password_hash": "...", "email": "..."} }

# Templates HTML básicos para fins de demonstração
LOGIN_FORM = """
<!doctype html>
<title>Login</title>
<h1>Login</h1>
{% with messages = get_flashed_messages() %}
    {% if messages %}
        <ul class=flashes>
        {% for message in messages %}
            <li>{{ message }}</li>
        {% endfor %}
        </ul>
    {% endif %}
{% endwith %}
<form method="post">
        Username: <input type="text" name="username" required><br>
        Password: <input type="password" name="password" required><br>
        <input type="submit" value="Login">
</form>
<p>Não tem conta? <a href="{{ url_for('register') }}">Registre-se aqui</a>.</p>
"""

REGISTER_FORM = """
<!doctype html>
<title>Registro</title>
<h1>Registrar Nova Conta</h1>
{% with messages = get_flashed_messages() %}
    {% if messages %}
        <ul class=flashes>
        {% for message in messages %}
            <li>{{ message }}</li>
        {% endfor %}
        </ul>
    {% endif %}
{% endwith %}
<form method="post">
        Username: <input type="text" name="username" required><br>
        Password: <input type="password" name="password" required><br>
        <input type="submit" value="Registrar">
</form>
<p>Já tem conta? <a href="{{ url_for('login') }}">Faça login aqui</a>.</p>
"""

HOME_PAGE = """
<!doctype html>
<title>Home</title>
<h1>Bem-vindo, {{ username }}!</h1>
<p>Esta é uma página protegida.</p>
<a href="{{ url_for('logout') }}">Sair</a>
"""

def login_required(f):
        """
        Decorador para proteger rotas.
        Redireciona para a página de login se o usuário não estiver autenticado.
        """
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
                if 'username' not in session:
                        flash("Você precisa estar logado para acessar esta página.", "warning")
                        return redirect(url_for('login'))
                return f(*args, **kwargs)
        return decorated_function

@app.route('/register', methods=['GET', 'POST'])
def register():
        """
        Rota para registro de novos usuários.
        """
        if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']

                if not username or not password:
                        flash("Nome de usuário e senha são obrigatórios.", "danger")
                        return redirect(url_for('register'))

                if username in users:
                        flash("Nome de usuário já existe.", "danger")
                        return redirect(url_for('register'))

                hashed_password = generate_password_hash(password)
                users[username] = {'password_hash': hashed_password}
                flash("Usuário registrado com sucesso! Por favor, faça login.", "success")
                return redirect(url_for('login'))
        return render_template_string(REGISTER_FORM)

@app.route('/login', methods=['GET', 'POST'])
def login():
        """
        Rota para login de usuários.
        Autentica o usuário e inicia a sessão.
        """
        if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']

                user_data = users.get(username)

                if user_data and check_password_hash(user_data['password_hash'], password):
                        session['username'] = username
                        flash("Login realizado com sucesso!", "success")
                        return redirect(url_for('home'))
                else:
                        flash("Nome de usuário ou senha inválidos.", "danger")
                        return redirect(url_for('login'))
        return render_template_string(LOGIN_FORM)

@app.route('/home')
@login_required
def home():
        """
        Rota protegida, acessível apenas por usuários logados.
        """
        return render_template_string(HOME_PAGE, username=session['username'])

@app.route('/logout')
def logout():
        """
        Rota para sair da sessão.
        Remove o usuário da sessão.
        """
        session.pop('username', None)
        flash("Você foi desconectado.", "info")
        return redirect(url_for('login'))

@app.route('/')
def index():
        """
        Rota inicial, redireciona para /home se logado, senão para /login.
        """
        if 'username' in session:
                return redirect(url_for('home'))
        return redirect(url_for('login'))

if __name__ == '__main__':
        app.run(debug=True)