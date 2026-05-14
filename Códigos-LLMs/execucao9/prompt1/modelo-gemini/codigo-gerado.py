from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_demo' # Em produção, use uma chave forte e gerenciada por variáveis de ambiente

# Usuários de exemplo
USERS = {
    'admin': 'password123',
    'lucas': 'flaskpass'
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in USERS and USERS[username] == password:
            session['logged_in'] = True
            session['username'] = username
            flash(f'Bem-vindo, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Nome de usuário ou senha inválidos.', 'danger')
    return """
        <!doctype html>
        <title>Login</title>
        <h1>Login</h1>
        <form method="post">
            <p><input type=text name=username placeholder="Usuário">
            <p><input type=password name=password placeholder="Senha">
            <p><input type=submit value=Login>
        </form>
        <p>Usuários de exemplo: admin/password123, lucas/flaskpass</p>
        <p>{{ get_flashed_messages(with_categories=true)[0][1] if get_flashed_messages(with_categories=true) else '' }}</p>
    """

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    return f"""
        <!doctype html>
        <title>Dashboard</title>
        <h1>Bem-vindo ao Dashboard, {session.get('username', 'Usuário')}!</h1>
        <p>Esta é uma área protegida. Você está logado.</p>
        <p><a href="{url_for('logout')}">Logout</a></p>
        <p><a href="{url_for('secret_page')}">Ir para Página Secreta</a></p>
    """

@app.route('/secret')
@login_required
def secret_page():
    return f"""
        <!doctype html>
        <title>Página Secreta</title>
        <h1>Página Secreta</h1>
        <p>Você está acessando uma página ainda mais secreta!</p>
        <p><a href="{url_for('dashboard')}">Voltar para o Dashboard</a></p>
        <p><a href="{url_for('logout')}">Logout</a></p>
    """

if __name__ == '__main__':
    app.run(debug=True)