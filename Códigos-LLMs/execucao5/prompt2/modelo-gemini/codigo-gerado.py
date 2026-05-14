from flask import Flask, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
# A secret key is required for session management
app.secret_key = os.urandom(24)

# Simulate a database of users
# In a real application, this would be a database like PostgreSQL, MySQL, etc.
users = {}  # {username: {'password': hashed_password}}

# Simple decorator to protect routes
def login_required(f):
    def wrapper(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            flash('Você precisa fazer login para acessar esta página.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__ # Preserve original function name
    return wrapper

@app.route('/')
def index():
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Usuário e senha são obrigatórios.', 'error')
            return redirect(url_for('register'))

        if username in users:
            flash('Usuário já existe. Por favor, escolha outro.', 'error')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        users[username] = {'password': hashed_password}
        flash('Registro realizado com sucesso! Por favor, faça login.', 'success')
        return redirect(url_for('login'))

    return '''
        <h1>Registrar</h1>
        <form method="post">
            <p>Nome de Usuário: <input type="text" name="username" required></p>
            <p>Senha: <input type="password" name="password" required></p>
            <p><input type="submit" value="Registrar"></p>
        </form>
        <p>Já tem uma conta? <a href="/login">Faça Login</a></p>
        '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users.get(username)

        if user and check_password_hash(user['password'], password):
            session['logged_in'] = True
            session['username'] = username
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Nome de usuário ou senha inválidos.', 'error')
            return redirect(url_for('login'))

    return '''
        <h1>Login</h1>
        <form method="post">
            <p>Nome de Usuário: <input type="text" name="username" required></p>
            <p>Senha: <input type="password" name="password" required></p>
            <p><input type="submit" value="Entrar"></p>
        </form>
        <p>Não tem uma conta? <a href="/register">Registrar</a></p>
        '''

@app.route('/home')
@login_required
def home():
    return f'''
        <h1>Bem-vindo, {session['username']}!</h1>
        <p>Esta é uma página protegida que você só pode ver após o login.</p>
        <p><a href="/logout">Sair</a></p>
        '''

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)