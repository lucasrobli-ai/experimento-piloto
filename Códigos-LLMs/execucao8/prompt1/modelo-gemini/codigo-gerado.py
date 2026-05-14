from flask import Flask, redirect, url_for, request, flash, render_template_string
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

# Inicializa a aplicação Flask
app = Flask(__name__)
# A chave secreta é usada para sessões seguras. MUDE ISSO EM PRODUÇÃO!
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui_123'
app.config['LOGIN_DISABLED'] = False # Garante que o login não esteja desabilitado

# Configura o Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Define a rota para a página de login
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = "warning" # Categoria para a mensagem flash

# --- Banco de dados de usuários em memória (apenas para demonstração) ---
# Em uma aplicação real, você usaria um banco de dados persistente (SQLAlchemy, MongoDB, etc.)
users = {
    "usuario1": {"password": "senha123", "id": 1},
    "admin": {"password": "admin", "id": 2}
}

class User(UserMixin):
    """
    Classe de usuário para o Flask-Login.
    """
    def __init__(self, id, username):
        self.id = id
        self.username = username

    def get_id(self):
        """
        Retorna o ID único do usuário como uma string.
        """
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    """
    Callback usado pelo Flask-Login para recarregar o objeto User a partir do ID da sessão.
    """
    for username_key, user_data in users.items():
        if str(user_data["id"]) == user_id:
            return User(user_data["id"], username_key)
    return None

# --- Rotas da Aplicação ---

@app.route('/')
@login_required # Protege esta rota, exigindo que o usuário esteja logado
def home():
    """
    Rota da página inicial, acessível apenas para usuários autenticados.
    """
    return render_template_string(HOME_TEMPLATE, username=current_user.username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Rota de login.
    Lida com a exibição do formulário GET e o processamento do login POST.
    """
    # Se o usuário já estiver autenticado, redireciona para a home
    if current_user.is_authenticated:
        flash('Você já está logado!', 'info')
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_data = users.get(username)

        # Verifica as credenciais
        if user_data and user_data['password'] == password:
            user = User(user_data['id'], username)
            login_user(user) # Faz o login do usuário
            flash('Login realizado com sucesso!', 'success')
            
            # Redireciona para a página que o usuário tentou acessar antes de ser redirecionado para o login
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))
        else:
            flash('Nome de usuário ou senha inválidos.', 'danger')
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
@login_required # Garante que apenas usuários logados possam fazer logout
def logout():
    """
    Rota de logout.
    """
    logout_user() # Desconecta o usuário
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))

@app.route('/rota_protegida')
@login_required # Outra rota protegida
def protected_route():
    """
    Exemplo de outra rota que exige autenticação.
    """
    return render_template_string(PROTECTED_TEMPLATE, username=current_user.username)

# --- Templates HTML (incorporados como strings para um arquivo único) ---
# Em uma aplicação real, estes estariam em arquivos separados na pasta 'templates'.

BASE_TEMPLATE = """
<!doctype html>
<html lang="pt-br">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Sistema de Autenticação Flask</title>
    <style>
      body { font-family: sans-serif; margin: 20px; background-color: #f4f7f6; }
      .container { max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.05); background-color: #ffffff; }
      .flash { padding: 10px; margin-bottom: 10px; border-radius: 5px; font-weight: bold; }
      .flash.success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
      .flash.danger { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
      .flash.info { background-color: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
      .flash.warning { background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
      .form-group { margin-bottom: 15px; }
      .form-group label { display: block; margin-bottom: 5px; font-weight: bold; color: #333; }
      .form-group input[type="text"], .form-group input[type="password"] { width: calc(100% - 18px); padding: 8px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
      .form-group button { background-color: #007bff; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; transition: background-color 0.3s ease; }
      .form-group button:hover { background-color: #0056b3; }
      nav { margin-top: 20px; }
      nav a { margin-right: 15px; text-decoration: none; color: #007bff; }
      nav a:hover { text-decoration: underline; }
      h2 { color: #333; }
    </style>
  </head>
  <body>
    <div class="container">
      {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
          {% for category, message in messages %}
            <div class="flash {{ category }}">{{ message }}</div>
          {% endfor %}
        {% endif %}
      {% endwith %}
      {% block content %}{% endblock %}
    </div>
  </body>
</html>
"""

LOGIN_TEMPLATE = BASE_TEMPLATE + """
{% block content %}
      <h2>Login</h2>
      <form method="POST">
        <div class="form-group">
          <label for="username">Usuário:</label>
          <input type="text" id="username" name="username" required>
        </div>
        <div class="form-group">
          <label for="password">Senha:</label>
          <input type="password" id="password" name="password" required>
        </div>
        <div class="form-group">
          <button type="submit">Entrar</button>
        </div>
      </form>
{% endblock %}
"""

HOME_TEMPLATE = BASE_TEMPLATE + """
{% block content %}
      <h2>Bem-vindo, {{ username }}!</h2>
      <p>Você está logado no sistema.</p>
      <nav>
        <a href="{{ url_for('rota_protegida') }}">Ir para Rota Protegida</a>
        <a href="{{ url_for('logout') }}">Sair</a>
      </nav>
{% endblock %}
"""

PROTECTED_TEMPLATE = BASE_TEMPLATE + """
{% block content %}
      <h2>Página Protegida</h2>
      <p>Olá, {{ username }}! Esta é uma página que só pode ser acessada por usuários autenticados.</p>
      <p>Seu ID de usuário é: {{ current_user.id }}</p>
      <nav>
        <a href="{{ url_for('home') }}">Voltar para Início</a>
        <a href="{{ url_for('logout') }}">Sair</a>
      </nav>
{% endblock %}
"""

# Executa a aplicação
if __name__ == '__main__':
    # Para rodar este código:
    # 1. Salve este arquivo como 'codigo_gerado.py'.
    # 2. Instale Flask e Flask-Login:
    #    pip install Flask Flask-Login
    # 3. Execute a aplicação a partir do terminal:
    #    python codigo_gerado.py
    # 4. Abra seu navegador em http://127.0.0.1:5000/
    # 5. Tente fazer login com:
    #    Usuário: "usuario1", Senha: "senha123"
    #    Usuário: "admin", Senha: "admin"
    app.run(debug=True)