from flask import Flask, redirect, url_for, request, flash, render_template_string
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

import uuid # Para gerar IDs de usuário únicos

app = Flask(__name__)
# A chave secreta é essencial para a segurança da sessão do Flask
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui_substitua_por_uma_string_aleatoria_e_longa_em_producao'
app.config['DEBUG'] = True # Desative em produção

# Configura o Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # A rota para a página de login
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'warning'

# --- Armazenamento de Usuários (em memória para este exemplo) ---
# Em uma aplicação real, você usaria um banco de dados (ex: SQLAlchemy)
users = {}  # Dicionário para armazenar objetos User por ID

class User(UserMixin):
    """Classe para representar um usuário, compatível com Flask-Login."""
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def get_id(self):
        """Retorna o ID único do usuário como string."""
        return str(self.id)

# Preenche com um usuário padrão para facilitar o teste
def create_default_user():
    if not any(u.username == 'testuser' for u in users.values()):
        user_id = str(uuid.uuid4())
        hashed_password = generate_password_hash('password123')
        default_user = User(user_id, 'testuser', hashed_password)
        users[user_id] = default_user
        print(f"Usuário padrão 'testuser' criado com senha 'password123'.")

# Garante que o usuário padrão seja criado ao iniciar o aplicativo
with app.app_context():
    create_default_user()

@login_manager.user_loader
def load_user(user_id):
    """
    Callback para recarregar o objeto User do user_id armazenado na sessão.
    Isso é necessário para que o Flask-Login possa gerenciar o usuário logado.
    """
    return users.get(user_id)

# --- Rotas da Aplicação ---

@app.route('/')
@login_required  # Esta rota exige que o usuário esteja autenticado
def index():
    """Página inicial protegida, visível apenas para usuários logados."""
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Página Inicial Protegida</title>
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        </head>
        <body>
            <div class="container mt-5">
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="alert alert-{{ category }}">{{ message }}</div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                <div class="card">
                    <div class="card-header">
                        <h2>Bem-vindo, {{ current_user.username }}!</h2>
                    </div>
                    <div class="card-body">
                        <p>Esta é uma página protegida. Você só pode vê-la porque está logado.</p>
                        <a href="{{ url_for('logout') }}" class="btn btn-danger">Sair</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
    ''', current_user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Rota para o login do usuário.
    - GET: Exibe o formulário de login.
    - POST: Processa as credenciais e tenta logar o usuário.
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((u for u in users.values() if u.username == username), None)

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login bem-sucedido!', 'success')
            next_page = request.args.get('next')  # Redireciona para a página que o usuário tentou acessar
            return redirect(next_page or url_for('index'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')

    return render_template_string('''
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Login</title>
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        </head>
        <body>
            <div class="container mt-5">
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="alert alert-{{ category }}">{{ message }}</div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                <div class="card">
                    <div class="card-header">
                        <h3>Login</h3>
                    </div>
                    <div class="card-body">
                        <form method="POST" action="{{ url_for('login') }}">
                            <div class="form-group">
                                <label for="username">Usuário:</label>
                                <input type="text" class="form-control" id="username" name="username" required>
                            </div>
                            <div class="form-group">
                                <label for="password">Senha:</label>
                                <input type="password" class="form-control" id="password" name="password" required>
                            </div>
                            <button type="submit" class="btn btn-primary">Entrar</button>
                        </form>
                        <p class="mt-3">Ainda não tem uma conta? <a href="{{ url_for('register') }}">Registre-se aqui</a>.</p>
                         <p class="mt-1"><small>Usuário de teste: <strong>testuser</strong>, Senha: <strong>password123</strong></small></p>
                    </div>
                </div>
            </div>
        </body>
        </html>
    ''')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Rota para o registro de novos usuários.
    - GET: Exibe o formulário de registro.
    - POST: Cria um novo usuário e armazena suas credenciais (hash de senha).
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Usuário e senha não podem ser vazios.', 'danger')
        elif any(u.username == username for u in users.values()):
            flash('Este nome de usuário já está em uso.', 'danger')
        else:
            user_id = str(uuid.uuid4()) # Gera um ID único para o novo usuário
            hashed_password = generate_password_hash(password)
            new_user = User(user_id, username, hashed_password)
            users[user_id] = new_user
            flash('Registro bem-sucedido! Por favor, faça login.', 'success')
            return redirect(url_for('login'))

    return render_template_string('''
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Registro</title>
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        </head>
        <body>
            <div class="container mt-5">
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="alert alert-{{ category }}">{{ message }}</div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                <div class="card">
                    <div class="card-header">
                        <h3>Registro de Nova Conta</h3>
                    </div>
                    <div class="card-body">
                        <form method="POST" action="{{ url_for('register') }}">
                            <div class="form-group">
                                <label for="username">Usuário:</label>
                                <input type="text" class="form-control" id="username" name="username" required>
                            </div>
                            <div class="form-group">
                                <label for="password">Senha:</label>
                                <input type="password" class="form-control" id="password" name="password" required>
                            </div>
                            <button type="submit" class="btn btn-success">Registrar</button>
                        </form>
                        <p class="mt-3">Já tem uma conta? <a href="{{ url_for('login') }}">Faça login aqui</a>.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
    ''')

@app.route('/logout')
@login_required # Garante que apenas usuários logados possam fazer logout
def logout():
    """Rota para desconectar o usuário."""
    logout_user()
    flash('Você foi desconectado com sucesso.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Para executar a aplicação, salve este código como um arquivo .py (ex: app.py)
    # e execute python app.py no terminal.
    # O aplicativo estará acessível em http://127.0.0.1:5000/
    app.run()