from flask import Flask, render_template_string, redirect, url_for, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_sessions' # Substitua por uma chave secreta forte em produção

# Simulação de um banco de dados de usuários
users = {} # username: hashed_password

# Decorador para rotas protegidas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('home'))
    return """
    <h1>Bem-vindo!</h1>
    <p><a href="/register">Registrar</a></p>
    <p><a href="/login">Login</a></p>
    """

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Usuário e senha são obrigatórios.', 'danger')
            return redirect(url_for('register'))

        if username in users:
            flash('Nome de usuário já existe. Por favor, escolha outro.', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        users[username] = hashed_password
        flash('Registro realizado com sucesso! Faça login agora.', 'success')
        return redirect(url_for('login'))
    return """
    <h1>Registro</h1>
    <form method="POST">
        <label for="username">Usuário:</label><br>
        <input type="text" id="username" name="username" required><br>
        <label for="password">Senha:</label><br>
        <input type="password" id="password" name="password" required><br><br>
        <input type="submit" value="Registrar">
    </form>
    <p><a href="/login">Já tem uma conta? Faça login.</a></p>
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        <ul class=flashes>
        {% for category, message in messages %}
          <li class="{{ category }}">{{ message }}</li>
        {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}
    """

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username not in users:
            flash('Usuário ou senha inválidos.', 'danger')
            return redirect(url_for('login'))

        if check_password_hash(users[username], password):
            session['logged_in'] = True
            session['username'] = username
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')
            return redirect(url_for('login'))
    return """
    <h1>Login</h1>
    <form method="POST">
        <label for="username">Usuário:</label><br>
        <input type="text" id="username" name="username" required><br>
        <label for="password">Senha:</label><br>
        <input type="password" id="password" name="password" required><br><br>
        <input type="submit" value="Entrar">
    </form>
    <p><a href="/register">Não tem uma conta? Registre-se.</a></p>
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        <ul class=flashes>
        {% for category, message in messages %}
          <li class="{{ category }}">{{ message }}</li>
        {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}
    """

@app.route('/home')
@login_required
def home():
    return f"""
    <h1>Bem-vindo, {session['username']}!</h1>
    <p>Esta é uma página protegida. Você está logado.</p>
    <p><a href="/logout">Sair</a></p>
    """

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)