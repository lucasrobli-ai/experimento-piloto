from flask import Flask, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'uma_chave_secreta_muito_segura' # Altere para uma chave secreta forte em produção

# Simulação de banco de dados de usuários
# Em um aplicativo real, você usaria um ORM como SQLAlchemy para interagir com um banco de dados.
users = {} # {'username': {'password_hash': '...', 'email': '...'}}

def login_required(f):
    """
    Decorador para rotas que exigem autenticação.
    Redireciona para a página de login se o usuário não estiver autenticado.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users:
            flash('Nome de usuário já existe.', 'danger')
        else:
            hashed_password = generate_password_hash(password)
            users[username] = {'password_hash': hashed_password}
            flash('Registro realizado com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
    
    return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Registrar</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .container { max-width: 400px; margin: auto; padding: 20px; border: 1px solid #ccc; border-radius: 5px; }
                input[type="text"], input[type="password"] { width: calc(100% - 20px); padding: 10px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 4px; }
                input[type="submit"] { background-color: #4CAF50; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; }
                input[type="submit"]:hover { background-color: #45a049; }
                .message { padding: 10px; margin-bottom: 10px; border-radius: 4px; }
                .success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
                .danger { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Registrar</h2>
                {% with messages = get_flashed_messages(with_categories=true) %}
                  {% if messages %}
                    {% for category, message in messages %}
                      <div class="message {{ category }}">{{ message }}</div>
                    {% endfor %}
                  {% endif %}
                {% endwith %}
                <form method="post">
                    <label for="username">Usuário:</label><br>
                    <input type="text" id="username" name="username" required><br>
                    <label for="password">Senha:</label><br>
                    <input type="password" id="password" name="password" required><br><br>
                    <input type="submit" value="Registrar">
                </form>
                <p>Já tem uma conta? <a href="/login">Faça login aqui</a></p>
            </div>
        </body>
        </html>
    """

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users.get(username)

        if user and check_password_hash(user['password_hash'], password):
            session['logged_in'] = True
            session['username'] = username
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Nome de usuário ou senha inválidos.', 'danger')
    
    return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .container { max-width: 400px; margin: auto; padding: 20px; border: 1px solid #ccc; border-radius: 5px; }
                input[type="text"], input[type="password"] { width: calc(100% - 20px); padding: 10px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 4px; }
                input[type="submit"] { background-color: #007bff; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; }
                input[type="submit"]:hover { background-color: #0056b3; }
                .message { padding: 10px; margin-bottom: 10px; border-radius: 4px; }
                .success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
                .danger { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
                .warning { background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Login</h2>
                {% with messages = get_flashed_messages(with_categories=true) %}
                  {% if messages %}
                    {% for category, message in messages %}
                      <div class="message {{ category }}">{{ message }}</div>
                    {% endfor %}
                  {% endif %}
                {% endwith %}
                <form method="post">
                    <label for="username">Usuário:</label><br>
                    <input type="text" id="username" name="username" required><br>
                    <label for="password">Senha:</label><br>
                    <input type="password" id="password" name="password" required><br><br>
                    <input type="submit" value="Entrar">
                </form>
                <p>Não tem uma conta? <a href="/register">Registre-se aqui</a></p>
            </div>
        </body>
        </html>
    """

@app.route('/home')
@login_required
def home():
    username = session.get('username')
    return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Home</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .container {{ max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ccc; border-radius: 5px; }}
                a {{ text-decoration: none; color: #007bff; margin-right: 15px; }}
                a:hover {{ text-decoration: underline; }}
                .message {{ padding: 10px; margin-bottom: 10px; border-radius: 4px; }}
                .success {{ background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
            </style>
        </head>
        <body>
            <div class="container">
                {% with messages = get_flashed_messages(with_categories=true) %}
                  {% if messages %}
                    {% for category, message in messages %}
                      <div class="message {{ category }}">{{ message }}</div>
                    {% endfor %}
                  {% endif %}
                {% endwith %}
                <h2>Bem-vindo, {username}!</h2>
                <p>Esta é a página inicial. Você está logado.</p>
                <p><a href="/protected">Acessar conteúdo protegido</a></p>
                <p><a href="/logout">Sair</a></p>
            </div>
        </body>
        </html>
    """

@app.route('/protected')
@login_required
def protected():
    return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Conteúdo Protegido</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .container {{ max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ccc; border-radius: 5px; }}
                a {{ text-decoration: none; color: #007bff; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Página Protegida</h2>
                <p>Você acessou conteúdo sensível. Parabéns!</p>
                <p><a href="/home">Voltar para a Home</a></p>
                <p><a href="/logout">Sair</a></p>
            </div>
        </body>
        </html>
    """

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Para testar, registre um usuário acessando /register primeiro.
    # Ex: usuário 'testuser', senha 'password123'
    app.run(debug=True)