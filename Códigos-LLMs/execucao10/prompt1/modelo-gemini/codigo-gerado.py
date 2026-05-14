from flask import Flask, request, redirect, url_for, session, flash, g
from functools import wraps

app = Flask(__name__)
app.secret_key = 'super_secret_key_change_me' # Substitua por uma chave secreta forte

# Usuários de exemplo (em um sistema real, viria de um banco de dados)
USERS = {
    'admin': 'password123',
    'lucas': 'senha123'
}

def login_required(f):
    """
    Decorador para proteger rotas que exigem autenticação.
    Redireciona para a página de login se o usuário não estiver autenticado.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def load_logged_in_user():
    """
    Carrega o usuário logado para o objeto 'g' (global) antes de cada requisição,
    se houver um usuário na sessão.
    """
    username = session.get('username')
    if username is None:
        g.user = None
    else:
        g.user = username # Em um sistema real, buscaríamos o objeto do usuário completo aqui

@app.route('/')
def index():
    """
    Redireciona para a dashboard se o usuário estiver logado,
    ou para a página de login caso contrário.
    """
    if g.user:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Rota para o login de usuário.
    - GET: Exibe o formulário de login.
    - POST: Processa as credenciais enviadas.
    """
    if g.user:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in USERS and USERS[username] == password:
            session['logged_in'] = True
            session['username'] = username
            flash(f'Login realizado com sucesso! Bem-vindo(a), {username}.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Nome de usuário ou senha inválidos.', 'danger')

    return """
        <!doctype html>
        <title>Login</title>
        <h1>Login</h1>
        <div style="color: red;">
            {% for message in get_flashed_messages(category_filter=['danger']) %}
                <p>{{ message }}</p>
            {% endfor %}
        </div>
        <div style="color: green;">
            {% for message in get_flashed_messages(category_filter=['success']) %}
                <p>{{ message }}</p>
            {% endfor %}
        </div>
        <div style="color: orange;">
            {% for message in get_flashed_messages(category_filter=['warning']) %}
                <p>{{ message }}</p>
            {% endfor %}
        </div>
        <form method="post">
            <p><label for="username">Usuário:</label> <input type="text" name="username" id="username" required></p>
            <p><label for="password">Senha:</label> <input type="password" name="password" id="password" required></p>
            <p><input type="submit" value="Entrar"></p>
        </form>
        <p>Usuários de teste: admin/password123, lucas/senha123</p>
    """

@app.route('/dashboard')
@login_required
def dashboard():
    """
    Rota protegida que só pode ser acessada por usuários logados.
    """
    return f"""
        <!doctype html>
        <title>Dashboard</title>
        <h1>Bem-vindo(a) à Dashboard, {g.user}!</h1>
        <div style="color: green;">
            {% for message in get_flashed_messages(category_filter=['success']) %}
                <p>{{ message }}</p>
            {% endfor %}
        </div>
        <p>Esta é uma página protegida. Você só pode vê-la porque está logado(a).</p>
        <p><a href="{url_for('logout')}">Sair</a></p>
        <p><a href="{url_for('profile')}">Ir para o perfil (outra rota protegida)</a></p>
    """

@app.route('/profile')
@login_required
def profile():
    """
    Outra rota protegida.
    """
    return f"""
        <!doctype html>
        <title>Perfil</title>
        <h1>Perfil de {g.user}</h1>
        <p>Esta é sua página de perfil. Somente usuários autenticados podem vê-la.</p>
        <p><a href="{url_for('dashboard')}">Voltar para a Dashboard</a></p>
        <p><a href="{url_for('logout')}">Sair</a></p>
    """

@app.route('/logout')
def logout():
    """
    Rota para realizar o logout do usuário.
    Limpa a sessão e redireciona para a página de login.
    """
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('Você foi desconectado(a).', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)