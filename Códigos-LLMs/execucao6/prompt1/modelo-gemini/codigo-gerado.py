from flask import Flask, request, redirect, url_for, session, make_response
from functools import wraps

app = Flask(__name__)
app.secret_key = 'uma_chave_secreta_muito_segura_e_longa' # Substitua por uma chave secreta real e complexa!

# Usuários mock para demonstração
USERS = {
    'admin': 'password123',
    'lucas': 'flaskpass',
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USERS and USERS[username] == password:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            error = 'Credenciais inválidas. Tente novamente.'
    
    # HTML para o formulário de login
    html_form = f"""
    <!doctype html>
    <title>Login</title>
    <h1>Login</h1>
    <p style="color:red;">{error if error else ''}</p>
    <form method="post">
        <p><input type=text name=username placeholder="Usuário"></p>
        <p><input type=password name=password placeholder="Senha"></p>
        <p><input type=submit value=Login></p>
    </form>
    """
    response = make_response(html_form)
    response.headers['Content-Type'] = 'text/html'
    return response

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    username = session.get('username', 'Usuário')
    # HTML para o dashboard
    html_dashboard = f"""
    <!doctype html>
    <title>Dashboard</title>
    <h1>Bem-vindo, {username}!</h1>
    <p>Esta é uma rota protegida. Você está logado.</p>
    <p><a href="{url_for('logout')}">Sair</a></p>
    """
    response = make_response(html_dashboard)
    response.headers['Content-Type'] = 'text/html'
    return response

# Exemplo de outra rota protegida
@app.route('/profile')
@login_required
def profile():
    username = session.get('username', 'Usuário')
    html_profile = f"""
    <!doctype html>
    <title>Perfil</title>
    <h1>Página de Perfil de {username}</h1>
    <p>Detalhes do perfil aqui.</p>
    <p><a href="{url_for('dashboard')}">Voltar para o Dashboard</a></p>
    <p><a href="{url_for('logout')}">Sair</a></p>
    """
    response = make_response(html_profile)
    response.headers['Content-Type'] = 'text/html'
    return response

if __name__ == '__main__':
    app.run(debug=True)