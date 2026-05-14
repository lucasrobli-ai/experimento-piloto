from flask import Flask, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key_here' # Substitua por uma chave secreta forte

# Simula um banco de dados de usuários
users = {} # username: hashed_password

def login_required(f):
    """
    Decorator para proteger rotas.
    Redireciona para a página de login se o usuário não estiver autenticado.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Redireciona para a página inicial ou login dependendo do estado da sessão."""
    if 'username' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Rota para registro de novos usuários.
    Permite criar um novo usuário com senha hashed.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Nome de usuário e senha são obrigatórios.', 'danger')
            return redirect(url_for('register'))

        if username in users:
            flash('Nome de usuário já existe. Por favor, escolha outro.', 'danger')
        else:
            hashed_password = generate_password_hash(password)
            users[username] = hashed_password
            flash('Registro bem-sucedido! Faça login agora.', 'success')
            return redirect(url_for('login'))
    
    return """
    <!doctype html>
    <title>Registrar</title>
    <h1>Registrar</h1>
    <form method="post">
        <p><input type=text name=username placeholder="Nome de Usuário">
        <p><input type=password name=password placeholder="Senha">
        <p><input type=submit value=Registrar>
    </form>
    <p>Já tem uma conta? <a href="/login">Faça Login</a></p>
    """ + "".join([f'<p style="color:red;">{message}</p>' for category, message in session.pop('_flashes', []) if category == 'danger']) + \
        "".join([f'<p style="color:green;">{message}</p>' for category, message in session.pop('_flashes', []) if category == 'success'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Rota para login de usuários.
    Verifica credenciais e estabelece a sessão do usuário.
    """
    if 'username' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_hashed_password = users.get(username)

        if user_hashed_password and check_password_hash(user_hashed_password, password):
            session['username'] = username
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Nome de usuário ou senha inválidos.', 'danger')
    
    return """
    <!doctype html>
    <title>Login</title>
    <h1>Login</h1>
    <form method="post">
        <p><input type=text name=username placeholder="Nome de Usuário">
        <p><input type=password name=password placeholder="Senha">
        <p><input type=submit value=Login>
    </form>
    <p>Não tem uma conta? <a href="/register">Registre-se</a></p>
    """ + "".join([f'<p style="color:red;">{message}</p>' for category, message in session.pop('_flashes', []) if category == 'danger']) + \
        "".join([f'<p style="color:green;">{message}</p>' for category, message in session.pop('_flashes', []) if category == 'success']) + \
        "".join([f'<p style="color:orange;">{message}</p>' for category, message in session.pop('_flashes', []) if category == 'warning'])


@app.route('/home')
@login_required
def home():
    """
    Rota protegida, acessível apenas para usuários logados.
    """
    username = session['username']
    return f"""
    <!doctype html>
    <title>Página Inicial</title>
    <h1>Bem-vindo, {username}!</h1>
    <p>Esta é uma área protegida.</p>
    <p><a href="/logout">Sair</a></p>
    """ + "".join([f'<p style="color:green;">{message}</p>' for category, message in session.pop('_flashes', []) if category == 'success'])


@app.route('/logout')
def logout():
    """
    Encerra a sessão do usuário e redireciona para a página de login.
    """
    session.pop('username', None)
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)