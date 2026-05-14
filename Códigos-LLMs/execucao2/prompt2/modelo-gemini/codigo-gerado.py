from flask import Flask, request, redirect, url_for, session, flash, escape, get_flashed_messages
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
# É crucial definir uma chave secreta forte para proteger as sessões.
# Em produção, esta chave deve ser uma string aleatória longa e mantida em segredo.
app.secret_key = 'sua_chave_secreta_muito_forte_aqui_em_producao' 

# Base de dados de usuários em memória (apenas para demonstração)
# Em uma aplicação real, você usaria um banco de dados persistente (e.g., SQLAlchemy com PostgreSQL/MySQL)
# Formato: { 'nome_de_usuario': { 'password_hash': 'senha_hash' } }
users = {}

# Decorador para proteger rotas.
# Somente usuários autenticados podem acessar rotas marcadas com este decorador.
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Função auxiliar para renderizar mensagens flash em respostas de string simples.
# Em uma aplicação real com templates Jinja2, isso seria feito diretamente no template.
def render_flashed_messages_html():
    messages_html = ""
    messages = get_flashed_messages(with_categories=True)
    if messages:
        messages_html = '<ul class="flashes">'
        for category, message in messages:
            messages_html += f'<li class="{escape(category)}">{escape(message)}</li>'
        messages_html += '</ul>'
    return messages_html

@app.route('/')
def index():
    """Redireciona para /home se logado, senão para /login."""
    if 'username' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Permite que novos usuários se registrem.
    As senhas são armazenadas como hash.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Nome de usuário e senha são obrigatórios.', 'danger')
            return redirect(url_for('register'))

        if username in users:
            flash('Nome de usuário já existe. Por favor, escolha outro.', 'danger')
            return redirect(url_for('register'))

        # Armazena a senha com hash para segurança
        hashed_password = generate_password_hash(password)
        users[username] = {'password_hash': hashed_password}
        flash('Registro realizado com sucesso! Por favor, faça login.', 'success')
        return redirect(url_for('login'))
    
    # Para requisições GET, exibe um formulário de registro simples
    return f'''
        <h1>Registrar</h1>
        {render_flashed_messages_html()}
        <form method="post">
            <p><label for="username">Nome de Usuário:</label><br><input type="text" id="username" name="username" required></p>
            <p><label for="password">Senha:</label><br><input type="password" id="password" name="password" required></p>
            <p><input type="submit" value="Registrar"></p>
        </form>
        <p>Já tem uma conta? <a href="/login">Faça login aqui</a>.</p>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Gerencia o processo de login do usuário.
    Verifica credenciais e estabelece a sessão.
    """
    if 'username' in session:
        return redirect(url_for('home')) # Já está logado, redireciona para a home

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users.get(username)

        # Verifica se o usuário existe e se a senha está correta
        if user and check_password_hash(user['password_hash'], password):
            session['username'] = username
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('home')) # Redireciona para /home após o login
        else:
            flash('Nome de usuário ou senha inválidos.', 'danger')
            return redirect(url_for('login'))
    
    # Para requisições GET, exibe um formulário de login simples
    return f'''
        <h1>Login</h1>
        {render_flashed_messages_html()}
        <form method="post">
            <p><label for="username">Nome de Usuário:</label><br><input type="text" id="username" name="username" required></p>
            <p><label for="password">Senha:</label><br><input type="password" id="password" name="password" required></p>
            <p><input type="submit" value="Login"></p>
        </form>
        <p>Não tem uma conta? <a href="/register">Registre-se aqui</a>.</p>
    '''

@app.route('/home')
@login_required # Esta rota é protegida e requer login
def home():
    """Página inicial acessível apenas para usuários logados."""
    username = session.get('username')
    return f'''
        <h1>Bem-vindo, {escape(username)}!</h1>
        <p>Esta é uma página protegida. Você está logado.</p>
        <p><a href="/logout">Sair</a></p>
    '''

@app.route('/logout')
def logout():
    """Finaliza a sessão do usuário e o redireciona para a página de login."""
    session.pop('username', None) # Remove o nome de usuário da sessão
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Ao executar em um ambiente de produção, desabilite o debug=True
    # e use um servidor WSGI como Gunicorn ou uWSGI.
    app.run(debug=True)