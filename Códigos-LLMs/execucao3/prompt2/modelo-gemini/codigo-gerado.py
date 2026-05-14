from flask import Flask, render_template_string, redirect, url_for, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
import functools

app = Flask(__name__)
# A secret key é usada para assinar cookies de sessão.
# É crucial que seja uma string longa e aleatória para segurança.
# Em produção, você deve carregá-la de uma variável de ambiente ou arquivo de configuração.
app.secret_key = os.urandom(24)

# Armazenamento de usuários em memória para demonstração.
# Em uma aplicação real, isso seria um banco de dados (ex: SQLite, PostgreSQL, MySQL).
# Estrutura: {username: {'password_hash': 'hashed_password_string'}}
users = {}

# Decorador para proteger rotas.
# Se o usuário não estiver logado, ele é redirecionado para a página de login.
def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Você precisa estar logado para acessar esta página.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Rota inicial. Redireciona para /home se logado, ou /login caso contrário.
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

# Rota para registro de novos usuários.
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Preencha todos os campos.')
            return redirect(url_for('register'))

        if username in users:
            flash('Nome de usuário já existe.')
            return redirect(url_for('register'))

        # Armazena a senha de forma segura (hash)
        hashed_password = generate_password_hash(password)
        users[username] = {'password_hash': hashed_password}
        flash('Registro realizado com sucesso! Por favor, faça login.')
        return redirect(url_for('login'))

    return render_template_string('''
        <!doctype html>
        <title>Registrar</title>
        <h1>Registrar</h1>
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
            <p><input type="text" name="username" placeholder="Usuário" required></p>
            <p><input type="password" name="password" placeholder="Senha" required></p>
            <p><input type="submit" value="Registrar"></p>
        </form>
        <p>Já tem uma conta? <a href="{{ url_for('login') }}">Faça login</a></p>
    ''')

# Rota para login de usuários.
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users.get(username)

        # Verifica se o usuário existe e se a senha está correta
        if user and check_password_hash(user['password_hash'], password):
            session['username'] = username  # Armazena o username na sessão
            flash('Login realizado com sucesso!')
            return redirect(url_for('home'))  # Redireciona para /home após login
        else:
            flash('Nome de usuário ou senha inválidos.')
            return redirect(url_for('login'))

    return render_template_string('''
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
            <p><input type="text" name="username" placeholder="Usuário" required></p>
            <p><input type="password" name="password" placeholder="Senha" required></p>
            <p><input type="submit" value="Entrar"></p>
        </form>
        <p>Não tem uma conta? <a href="{{ url_for('register') }}">Registre-se</a></p>
    ''')

# Rota para logout do usuário.
@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove o username da sessão
    flash('Você foi desconectado.')
    return redirect(url_for('login'))

# Rota da página inicial (protegida).
@app.route('/home')
@login_required  # Aplica o decorador para proteger a rota
def home():
    return render_template_string(f'''
        <!doctype html>
        <title>Home</title>
        <h1>Bem-vindo, {session.get('username')}!</h1>
        <p>Esta é a página inicial protegida.</p>
        <p><a href="{url_for('protected')}">Ir para uma página ainda mais protegida</a></p>
        <p><a href="{url_for('logout')}">Sair</a></p>
    ''')

# Exemplo de outra rota protegida.
@app.route('/protected')
@login_required  # Aplica o decorador para proteger a rota
def protected():
    return render_template_string(f'''
        <!doctype html>
        <title>Página Protegida</title>
        <h1>Página Protegida</h1>
        <p>Olá, {session.get('username')}. Você está acessando uma rota que requer autenticação.</p>
        <p><a href="{url_for('home')}">Voltar para Home</a></p>
        <p><a href="{url_for('logout')}">Sair</a></p>
    ''')

if __name__ == '__main__':
    # 'debug=True' habilita o modo de depuração, que recarrega o servidor
    # automaticamente e fornece um depurador no navegador.
    # Desative em produção.
    app.run(debug=True)