from flask import Flask, request, redirect, url_for, session, flash, escape
from functools import wraps

app = Flask(__name__)
app.secret_key = 'super_secreto_e_aleatorio_chave' # Substitua por uma chave secreta forte e aleatória

# Usuários de exemplo (substitua por um banco de dados real e senhas hash)
USERS = {
    'admin': 'senha123',
    'lucas': 'minhasenha'
}

def login_required(f):
    """
    Decorator para rotas que exigem autenticação.
    Redireciona para a página de login se o usuário não estiver logado.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            flash('Por favor, faça login para acessar esta página.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Rota para o login do usuário.
    GET: Exibe o formulário de login.
    POST: Processa as credenciais e tenta logar o usuário.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in USERS and USERS[username] == password:
            session['logged_in'] = True
            session['username'] = username
            flash(f'Login realizado com sucesso, {username}!')
            return redirect(url_for('home'))
        else:
            flash('Credenciais inválidas. Tente novamente.')
    
    # Formulário de login para GET e para falha de POST
    return '''
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
            <p><input type=text name=username placeholder="Usuário">
            <p><input type=password name=password placeholder="Senha">
            <p><input type=submit value=Login>
        </form>
    '''

@app.route('/logout')
def logout():
    """
    Rota para fazer logout.
    Limpa a sessão e redireciona para a página de login.
    """
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('Você foi desconectado.')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    """
    Rota inicial, acessível apenas após o login.
    Exibe uma mensagem de boas-vindas e um link para logout.
    """
    return f'''
        <!doctype html>
        <title>Página Inicial</title>
        <h1>Bem-vindo, {escape(session.get('username', ''))}!</h1>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <ul class=flashes>
            {% for message in messages %}
              <li>{{ message }}</li>
            {% endfor %}
            </ul>
          {% endif %}
        {% endwith %}
        <p>Esta é uma página protegida.
        <p><a href="/dashboard">Ir para o Dashboard</a></p>
        <p><a href="/logout">Logout</a></p>
    '''

@app.route('/dashboard')
@login_required
def dashboard():
    """
    Outra rota protegida, acessível apenas após o login.
    """
    return f'''
        <!doctype html>
        <title>Dashboard</title>
        <h1>Dashboard</h1>
        <p>Bem-vindo ao seu dashboard, {escape(session.get('username', ''))}!</p>
        <p>Aqui você pode ver informações importantes.</p>
        <p><a href="/">Voltar para a Página Inicial</a></p>
        <p><a href="/logout">Logout</a></p>
    '''

if __name__ == '__main__':
    # Para executar, use 'flask run' ou descomente a linha abaixo.
    # Em produção, use um servidor WSGI como Gunicorn ou uWSGI.
    app.run(debug=True)