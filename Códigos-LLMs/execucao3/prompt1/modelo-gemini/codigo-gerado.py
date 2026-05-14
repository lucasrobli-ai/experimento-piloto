from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from functools import wraps

app = Flask(__name__)
# É essencial definir uma chave secreta para a segurança das sessões.
# Substitua 'sua_chave_secreta_aqui' por uma string aleatória e complexa.
app.secret_key = 'sua_chave_secreta_aqui_substitua_por_uma_forte_e_aleatoria'

# Banco de dados de usuários fictício para demonstração
# Em uma aplicação real, você usaria um banco de dados e senhas criptografadas.
USERS = {
    "admin": "admin123",
    "user": "user123",
    "lucas": "senha123"
}

# Decorador para exigir que o usuário esteja logado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            flash('Por favor, faça login para acessar esta página.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Rota principal - redireciona para login ou para o dashboard se já estiver logado
@app.route('/')
def index():
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Rota de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in USERS and USERS[username] == password:
            session['logged_in'] = True
            session['username'] = username  # Armazena o nome de usuário na sessão
            flash(f'Bem-vindo, {username}! Login realizado com sucesso.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciais inválidas. Por favor, tente novamente.', 'danger')
    
    # HTML para o formulário de login (incorporado para simplificar o exemplo em um único arquivo)
    login_form_html = """
    <!doctype html>
    <html lang="pt-br">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>Login no Sistema</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; background-color: #e9ecef; margin: 0; }
            .container { background: white; padding: 35px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
            h2 { text-align: center; color: #343a40; margin-bottom: 25px; }
            .flash-message { padding: 12px; margin-bottom: 18px; border-radius: 6px; font-weight: bold; }
            .flash-message.danger { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            .flash-message.success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            label { display: block; margin-bottom: 8px; color: #495057; font-weight: 600; }
            input[type="text"], input[type="password"] { width: calc(100% - 24px); padding: 12px; margin-bottom: 18px; border: 1px solid #ced4da; border-radius: 6px; box-sizing: border-box; font-size: 16px; }
            input[type="text"]:focus, input[type="password"]:focus { border-color: #80bdff; outline: 0; box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25); }
            button { width: 100%; padding: 12px; background-color: #007bff; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 18px; font-weight: bold; transition: background-color 0.3s ease; }
            button:hover { background-color: #0056b3; }
            p.info { text-align: center; margin-top: 25px; color: #6c757d; font-size: 0.9em; line-height: 1.5; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Acesso ao Sistema</h2>
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="flash-message {{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            <form method="POST">
                <div>
                    <label for="username">Usuário:</label>
                    <input type="text" id="username" name="username" required autocomplete="username">
                </div>
                <div>
                    <label for="password">Senha:</label>
                    <input type="password" id="password" name="password" required autocomplete="current-password">
                </div>
                <button type="submit">Entrar</button>
            </form>
            <p class="info">
                Usuários de teste:<br>
                <b>admin</b> / admin123<br>
                <b>user</b> / user123<br>
                <b>lucas</b> / senha123
            </p>
        </div>
    </body>
    </html>
    """
    return render_template_string(login_form_html)

# Rota de Logout
@app.route('/logout')
@login_required # Opcional, mas boa prática para garantir que apenas logados possam "deslogar"
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('Você foi desconectado com sucesso.', 'info')
    return redirect(url_for('login'))

# Rota protegida (Dashboard)
@app.route('/dashboard')
@login_required # Aplica o decorador para proteger esta rota
def dashboard():
    username = session.get('username', 'Usuário') # Pega o nome de usuário da sessão
    # HTML para o dashboard (incorporado para simplificar o exemplo em um único arquivo)
    dashboard_html = f"""
    <!doctype html>
    <html lang="pt-br">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>Dashboard</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; flex-direction: column; justify-content: center; align-items: center; min-height: 100vh; background-color: #e9ecef; margin: 0; }}
            .container {{ background: white; padding: 35px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); width: 100%; max-width: 600px; text-align: center; }}
            h1 {{ color: #343a40; margin-bottom: 20px; }}
            p {{ color: #495057; margin-bottom: 30px; font-size: 1.1em; }}
            .flash-message {{ padding: 12px; margin-bottom: 18px; border-radius: 6px; font-weight: bold; }}
            .flash-message.info {{ background-color: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
            .logout-btn {{ display: inline-block; padding: 10px 20px; background-color: #dc3545; color: white; border-radius: 6px; text-decoration: none; font-weight: bold; transition: background-color 0.3s ease; }}
            .logout-btn:hover {{ background-color: #c82333; }}
        </style>
    </head>
    <body>
        <div class="container">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="flash-message {{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            <h1>Bem-vindo ao Dashboard, {username}!</h1>
            <p>Você acessou uma área protegida do sistema.</p>
            <a href="{url_for('logout')}" class="logout-btn">Sair</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(dashboard_html.format(username=username, url_for=url_for))

if __name__ == '__main__':
    # Em produção, debug=False e use um servidor WSGI como Gunicorn.
    app.run(debug=True)