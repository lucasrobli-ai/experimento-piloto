from flask import Flask, request, redirect, url_for, session, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
# A chave secreta é essencial para a segurança das sessões do Flask.
# Em um ambiente de produção, esta chave deve ser gerada de forma segura
# e carregada de uma variável de ambiente ou arquivo de configuração.
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'uma_chave_secreta_muito_segura_e_longa_aqui')

# Banco de dados de usuários simulado em memória
# Em uma aplicação real, você usaria um banco de dados persistente (SQLAlchemy, MongoDB, etc.)
users_db = {}

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            return make_response("Usuário e senha são obrigatórios.", 400)

        if username in users_db:
            return make_response("Nome de usuário já existe.", 409)

        hashed_password = generate_password_hash(password)
        users_db[username] = {'password_hash': hashed_password}
        print(f"Usuário '{username}' registrado com sucesso.")
        return redirect(url_for('login'))
    
    # Simples formulário de registro (para fins de demonstração, sem HTML real)
    return """
        <h1>Registro</h1>
        <form method="post">
            <p><input type="text" name="username" placeholder="Usuário"></p>
            <p><input type="password" name="password" placeholder="Senha"></p>
            <p><input type="submit" value="Registrar"></p>
        </form>
        <p>Já tem uma conta? <a href="/login">Faça login</a></p>
    """

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users_db.get(username)

        if user and check_password_hash(user['password_hash'], password):
            session['logged_in'] = True
            session['username'] = username
            print(f"Usuário '{username}' logado com sucesso.")
            return redirect(url_for('home'))
        else:
            return make_response("Usuário ou senha inválidos.", 401)
    
    # Simples formulário de login (para fins de demonstração, sem HTML real)
    return """
        <h1>Login</h1>
        <form method="post">
            <p><input type="text" name="username" placeholder="Usuário"></p>
            <p><input type="password" name="password" placeholder="Senha"></p>
            <p><input type="submit" value="Login"></p>
        </form>
        <p>Não tem uma conta? <a href="/register">Registre-se</a></p>
    """

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    print("Usuário deslogado.")
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'logged_in' in session and session['logged_in']:
        username = session['username']
        return f"""
            <h1>Bem-vindo, {username}!</h1>
            <p>Esta é a página inicial protegida.</p>
            <p><a href="/protected">Ir para página protegida</a></p>
            <p><a href="/logout">Sair</a></p>
        """
    return redirect(url_for('login'))

@app.route('/protected')
def protected():
    if 'logged_in' in session and session['logged_in']:
        username = session['username']
        return f"""
            <h1>Olá, {username}!</h1>
            <p>Esta é uma outra rota protegida.</p>
            <p><a href="/home">Voltar para a Home</a></p>
            <p><a href="/logout">Sair</a></p>
        """
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Para executar: python your_app_name.py
    # Acesse http://127.0.0.1:5000/
    # Certifique-se de definir a variável de ambiente FLASK_SECRET_KEY
    # ou mude 'uma_chave_secreta_muito_segura_e_longa_aqui' para algo único e complexo.
    app.run(debug=True)